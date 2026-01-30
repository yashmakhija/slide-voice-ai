import { create } from "zustand";
import { useShallow } from "zustand/shallow";
import type { Slide, VoiceState } from "@/types";

interface PresentationState {
  slides: Slide[];
  currentIndex: number;
  voiceState: VoiceState;
  isLoading: boolean;
  error: string | null;
}

interface PresentationActions {
  fetchSlides: () => Promise<void>;
  next: () => void;
  prev: () => void;
  goToSlide: (index: number) => void;
  setVoiceState: (state: VoiceState) => void;
  reset: () => void;
}

type PresentationStore = PresentationState & PresentationActions;

const initialState: PresentationState = {
  slides: [],
  currentIndex: 0,
  voiceState: "idle",
  isLoading: false,
  error: null,
};

export const usePresentationStore = create<PresentationStore>((set, get) => ({
  ...initialState,

  fetchSlides: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch("/api/slides");
      if (!response.ok) {
        throw new Error(`Failed to fetch slides: ${response.statusText}`);
      }
      const slides = await response.json();
      set({ slides, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      set({ error: message, isLoading: false });
    }
  },

  next: () => {
    const { currentIndex, slides } = get();
    if (currentIndex < slides.length - 1) {
      set({ currentIndex: currentIndex + 1 });
    }
  },

  prev: () => {
    const { currentIndex } = get();
    if (currentIndex > 0) {
      set({ currentIndex: currentIndex - 1 });
    }
  },

  goToSlide: (index: number) => {
    const { slides } = get();
    if (index >= 0 && index < slides.length) {
      set({ currentIndex: index });
    }
  },

  setVoiceState: (voiceState: VoiceState) => {
    set({ voiceState });
  },

  reset: () => {
    set(initialState);
  },
}));

export const useCurrentSlide = () =>
  usePresentationStore((state) =>
    state.slides.length > 0 ? state.slides[state.currentIndex] : null
  );

export const useCanNavigate = () =>
  usePresentationStore(
    useShallow((state) => ({
      canPrev: state.currentIndex > 0,
      canNext: state.currentIndex < state.slides.length - 1,
    }))
  );
