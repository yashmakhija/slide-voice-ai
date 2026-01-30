import { motion, AnimatePresence } from "framer-motion";
import { Brain, Layers, Globe, Zap, Rocket, type LucideIcon } from "lucide-react";
import { useCurrentSlide, usePresentationStore } from "@/stores";

const iconMap: Record<string, LucideIcon> = {
  brain: Brain,
  layers: Layers,
  globe: Globe,
  zap: Zap,
  rocket: Rocket,
};

interface SlideViewProps {
  isLoading?: boolean;
}

export function SlideView({ isLoading = false }: SlideViewProps) {
  const slide = useCurrentSlide();
  const currentIndex = usePresentationStore((s) => s.currentIndex);
  const totalSlides = usePresentationStore((s) => s.slides.length);

  if (isLoading || !slide) {
    return (
      <div className="w-full max-w-2xl mx-auto px-6 py-20">
        <div className="flex items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      </div>
    );
  }

  const IconComponent = iconMap[slide.iconName || "layers"] || Layers;

  return (
    <div className="w-full max-w-2xl mx-auto px-6">
      <AnimatePresence mode="wait">
        <motion.article
          key={slide.id}
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -24 }}
          transition={{ duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
        >
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-[11px] font-medium text-primary tracking-[0.2em] uppercase mb-8"
          >
            {String(currentIndex + 1).padStart(2, "0")} of {String(totalSlides).padStart(2, "0")}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15, type: "spring", stiffness: 300, damping: 20 }}
            className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center mb-8"
          >
            <IconComponent className="w-5 h-5 text-primary-foreground" strokeWidth={2} />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-[28px] sm:text-[36px] lg:text-[42px] font-semibold text-foreground leading-[1.1] tracking-[-0.02em] mb-10"
          >
            {slide.title}
          </motion.h1>

          <ul className="space-y-5">
            {slide.content.map((item, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.08 }}
                className="flex gap-4"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-3 flex-shrink-0" />
                <p className="text-[15px] sm:text-[17px] text-muted-foreground leading-[1.7]">
                  {item}
                </p>
              </motion.li>
            ))}
          </ul>
        </motion.article>
      </AnimatePresence>
    </div>
  );
}
