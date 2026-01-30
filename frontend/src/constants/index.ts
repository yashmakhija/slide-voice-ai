export const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const AUDIO_CONFIG = {
  sampleRate: 24000,
  channelCount: 1,
  bufferSize: 4096,
} as const;
