import { useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";
import { usePresentationStore, useCanNavigate } from "@/stores";

export function SlideControls() {
  const next = usePresentationStore((s) => s.next);
  const prev = usePresentationStore((s) => s.prev);
  const currentIndex = usePresentationStore((s) => s.currentIndex);
  const totalSlides = usePresentationStore((s) => s.slides.length);
  const { canPrev, canNext } = useCanNavigate();

  const handleNext = useCallback(() => {
    if (canNext) next();
  }, [canNext, next]);

  const handlePrev = useCallback(() => {
    if (canPrev) prev();
  }, [canPrev, prev]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;
      if (e.key === "ArrowRight") {
        e.preventDefault();
        handleNext();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        handlePrev();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleNext, handlePrev]);

  if (totalSlides === 0) return null;

  return (
    <motion.nav
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.6 }}
      className="fixed bottom-0 left-0 right-0 z-20 pb-6 sm:pb-8 bg-gradient-to-t from-background via-background/80 to-transparent pt-8"
      aria-label="Slide navigation"
    >
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={handlePrev}
          disabled={!canPrev}
          aria-label="Previous slide"
          className="w-10 h-10 rounded-full border border-border bg-background flex items-center justify-center transition-all duration-200 hover:border-primary hover:text-primary active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 min-w-[100px] justify-center" role="tablist">
          {Array.from({ length: totalSlides }).map((_, i) => (
            <span
              key={i}
              role="tab"
              aria-selected={i === currentIndex}
              className={`block rounded-full transition-all duration-300 ${
                i === currentIndex
                  ? "w-6 h-1.5 bg-primary"
                  : "w-1.5 h-1.5 bg-muted-foreground/40"
              }`}
            />
          ))}
        </div>

        <button
          onClick={handleNext}
          disabled={!canNext}
          aria-label="Next slide"
          className="w-10 h-10 rounded-full border border-border bg-background flex items-center justify-center transition-all duration-200 hover:border-primary hover:text-primary active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </motion.nav>
  );
}
