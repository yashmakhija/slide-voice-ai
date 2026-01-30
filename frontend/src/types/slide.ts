export interface Slide {
  id: number;
  title: string;
  content: string[];
  narration: string;
}

export interface SlideState {
  currentSlide: Slide | null;
  totalSlides: number;
  hasNext: boolean;
  hasPrevious: boolean;
}
