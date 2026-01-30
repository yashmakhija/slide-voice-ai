import { motion } from "framer-motion";
import { VoiceIndicator } from "./VoiceIndicator";
import { useVoiceSession } from "@/contexts";
import { usePresentationStore } from "@/stores";

export function Header() {
  const voiceState = usePresentationStore((s) => s.voiceState);
  const { isActive, start, stop } = useVoiceSession();

  const handleClick = () => {
    if (isActive) {
      stop();
    } else {
      start();
    }
  };

  return (
    <motion.header
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed top-0 left-0 right-0 z-10 flex justify-center py-4 sm:py-5 bg-gradient-to-b from-background via-background/90 to-transparent pb-8"
    >
      <VoiceIndicator
        isActive={isActive}
        isSpeaking={voiceState === "speaking"}
        isListening={voiceState === "listening"}
        isProcessing={voiceState === "processing"}
        onClick={handleClick}
      />
    </motion.header>
  );
}
