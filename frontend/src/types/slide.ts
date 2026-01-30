export interface Slide {
  id: number;
  title: string;
  content: string[];
  narration: string;
  iconName?: "brain" | "layers" | "globe" | "zap" | "rocket";
}
