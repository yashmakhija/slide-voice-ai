import { motion } from "framer-motion";
import { VoiceIndicator } from "./VoiceIndicator";
import { usePresentationStore } from "@/stores";

export function Header() {
  const voiceState = usePresentationStore((s) => s.voiceState);

  return (
    <motion.header
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed top-0 left-0 right-0 z-10 flex justify-center py-5"
    >
      <VoiceIndicator
        isSpeaking={voiceState === "speaking"}
        isListening={voiceState === "listening"}
      />
    </motion.header>
  );
}
