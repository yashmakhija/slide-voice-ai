export interface StartSessionEvent {
  type: "session.start";
}

export interface StopSessionEvent {
  type: "session.stop";
}

export interface AudioInputEvent {
  type: "audio.input";
  audio: string; // Base64 encoded PCM16
}

export interface NavigateEvent {
  type: "slide.navigate";
  direction: "next" | "prev";
}

export interface GoToSlideEvent {
  type: "slide.goto";
  slide_id: number;
}

export interface CancelResponseEvent {
  type: "response.cancel";
}

export type ClientEvent =
  | StartSessionEvent
  | StopSessionEvent
  | AudioInputEvent
  | NavigateEvent
  | GoToSlideEvent
  | CancelResponseEvent;

export interface SessionStartedEvent {
  type: "session.started";
  session_id: string;
}

export interface SessionStoppedEvent {
  type: "session.stopped";
}

export interface AudioOutputEvent {
  type: "audio.output";
  audio: string; // Base64 encoded PCM16
}

export interface AudioDoneEvent {
  type: "audio.done";
}

export interface SlideChangedEvent {
  type: "slide.changed";
  slide_id: number;
  title: string;
  content: string[];
  narration: string;
  total_slides: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface TranscriptEvent {
  type: "transcript";
  text: string;
  is_final: boolean;
  speaker: "user" | "ai";
}

export interface ErrorEvent {
  type: "error";
  message: string;
  code?: string;
}

export interface ConnectionStatusEvent {
  type: "connection.status";
  status: "connecting" | "connected" | "disconnected" | "error";
  message?: string;
}

export type ServerEvent =
  | SessionStartedEvent
  | SessionStoppedEvent
  | AudioOutputEvent
  | AudioDoneEvent
  | SlideChangedEvent
  | TranscriptEvent
  | ErrorEvent
  | ConnectionStatusEvent;
