import { createContext, useContext, useCallback, useRef, useState, type ReactNode } from "react";
import { usePresentationStore } from "@/stores";

interface VoiceSessionContextType {
  isActive: boolean;
  error: string | null;
  start: () => Promise<void>;
  stop: () => void;
}

const VoiceSessionContext = createContext<VoiceSessionContextType | null>(null);

const SAMPLE_RATE = 24000;
const BUFFER_SIZE = 4800;

export function VoiceSessionProvider({ children }: { children: ReactNode }) {
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const playbackContextRef = useRef<AudioContext | null>(null);
  const nextPlayTimeRef = useRef<number>(0);
  const isActiveRef = useRef(false);

  const setVoiceState = usePresentationStore((s) => s.setVoiceState);
  const goToSlide = usePresentationStore((s) => s.goToSlide);

  const playAudio = useCallback((base64Audio: string) => {
    if (!playbackContextRef.current) {
      playbackContextRef.current = new AudioContext({ sampleRate: SAMPLE_RATE });
    }

    const ctx = playbackContextRef.current;
    if (ctx.state === "suspended") ctx.resume();

    const pcm16 = base64ToInt16Array(base64Audio);
    const float32 = new Float32Array(pcm16.length);
    for (let i = 0; i < pcm16.length; i++) {
      float32[i] = pcm16[i] / 32768;
    }

    const buffer = ctx.createBuffer(1, float32.length, SAMPLE_RATE);
    buffer.getChannelData(0).set(float32);

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    const startTime = Math.max(ctx.currentTime, nextPlayTimeRef.current);
    source.start(startTime);
    nextPlayTimeRef.current = startTime + buffer.duration;
  }, []);

  const cleanup = useCallback(() => {
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }

    if (playbackContextRef.current) {
      playbackContextRef.current.close();
      playbackContextRef.current = null;
    }
    nextPlayTimeRef.current = 0;
  }, []);

  const stop = useCallback(() => {
    console.log("Stopping voice session");
    isActiveRef.current = false;

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "session.stop" }));
      wsRef.current.close();
    }
    wsRef.current = null;

    cleanup();
    setIsActive(false);
    setVoiceState("idle");
  }, [cleanup, setVoiceState]);

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      console.log("Received:", data.type);

      switch (data.type) {
        case "session.started":
          console.log("Session started:", data.session_id);
          setVoiceState("speaking");
          break;

        case "session.stopped":
          setVoiceState("idle");
          break;

        case "audio.output":
          playAudio(data.audio);
          setVoiceState("speaking");
          break;

        case "audio.done":
          setVoiceState("listening");
          break;

        case "audio.interrupted":
          // Stop any queued audio playback
          if (playbackContextRef.current) {
            playbackContextRef.current.close();
            playbackContextRef.current = null;
            nextPlayTimeRef.current = 0;
          }
          setVoiceState("listening");
          break;

        case "slide.changed":
          console.log("Slide changed to:", data.slide_id);
          goToSlide(data.slide_id - 1);
          break;

        case "transcript":
          console.log(`[${data.speaker}]: ${data.text}`);
          break;

        case "error":
          console.error("Server error:", data.message);
          setError(data.message);
          break;
      }
    } catch (e) {
      console.error("Failed to parse message:", e);
    }
  }, [setVoiceState, goToSlide, playAudio]);

  const startAudioCapture = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: SAMPLE_RATE,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });
    streamRef.current = stream;

    const ctx = new AudioContext({ sampleRate: SAMPLE_RATE });
    audioContextRef.current = ctx;

    await ctx.audioWorklet.addModule(
      URL.createObjectURL(
        new Blob([`
          class CaptureProcessor extends AudioWorkletProcessor {
            constructor() {
              super();
              this.buffer = [];
            }
            process(inputs) {
              const input = inputs[0];
              if (input.length > 0) {
                const samples = input[0];
                for (let i = 0; i < samples.length; i++) {
                  this.buffer.push(samples[i]);
                }
                while (this.buffer.length >= ${BUFFER_SIZE}) {
                  const chunk = this.buffer.splice(0, ${BUFFER_SIZE});
                  const pcm16 = new Int16Array(chunk.length);
                  for (let i = 0; i < chunk.length; i++) {
                    const s = Math.max(-1, Math.min(1, chunk[i]));
                    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
                  }
                  this.port.postMessage(pcm16.buffer, [pcm16.buffer]);
                }
              }
              return true;
            }
          }
          registerProcessor('capture-processor', CaptureProcessor);
        `], { type: "application/javascript" })
      )
    );

    const source = ctx.createMediaStreamSource(stream);
    const worklet = new AudioWorkletNode(ctx, "capture-processor");

    worklet.port.onmessage = (e) => {
      if (wsRef.current?.readyState === WebSocket.OPEN && isActiveRef.current) {
        const base64 = arrayBufferToBase64(e.data);
        wsRef.current.send(JSON.stringify({ type: "audio.input", audio: base64 }));
      }
    };

    source.connect(worklet);
    workletNodeRef.current = worklet;
  }, []);

  const start = useCallback(async () => {
    if (isActiveRef.current) {
      console.log("Already active, ignoring start");
      return;
    }

    try {
      setError(null);
      setVoiceState("processing");
      console.log("Starting voice session...");

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
      wsRef.current = ws;

      await new Promise<void>((resolve, reject) => {
        ws.onopen = () => {
          console.log("WebSocket connected");
          resolve();
        };
        ws.onerror = (e) => {
          console.error("WebSocket error:", e);
          reject(new Error("WebSocket connection failed"));
        };
        setTimeout(() => reject(new Error("Connection timeout")), 10000);
      });

      ws.onmessage = handleMessage;

      ws.onclose = () => {
        console.log("WebSocket closed");
        if (isActiveRef.current) {
          isActiveRef.current = false;
          setIsActive(false);
          setVoiceState("idle");
          cleanup();
        }
      };

      await startAudioCapture();
      console.log("Audio capture started");

      ws.send(JSON.stringify({ type: "session.start" }));
      console.log("Session start sent");

      isActiveRef.current = true;
      setIsActive(true);
    } catch (err) {
      console.error("Start failed:", err);
      const message = err instanceof Error ? err.message : "Failed to start";
      setError(message);
      setVoiceState("idle");
      isActiveRef.current = false;
      setIsActive(false);
      cleanup();
    }
  }, [handleMessage, startAudioCapture, setVoiceState, cleanup]);

  return (
    <VoiceSessionContext.Provider value={{ isActive, error, start, stop }}>
      {children}
    </VoiceSessionContext.Provider>
  );
}

export function useVoiceSession() {
  const context = useContext(VoiceSessionContext);
  if (!context) {
    throw new Error("useVoiceSession must be used within VoiceSessionProvider");
  }
  return context;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToInt16Array(base64: string): Int16Array {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Int16Array(bytes.buffer);
}
