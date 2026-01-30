import { motion } from "framer-motion";
import { Mic } from "lucide-react";

interface VoiceIndicatorProps {
  isSpeaking: boolean;
  isListening: boolean;
}

export function VoiceIndicator({ isSpeaking, isListening }: VoiceIndicatorProps) {
  const isActive = isSpeaking || isListening;

  return (
    <div className="flex items-center gap-3">
      <div className="relative">
        {isActive && (
          <motion.span
            className="absolute inset-0 rounded-full bg-primary"
            initial={{ scale: 1, opacity: 0.4 }}
            animate={{ scale: 2, opacity: 0 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
          />
        )}
        <motion.div
          className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-colors duration-300 ${
            isActive ? "bg-primary" : "bg-muted"
          }`}
          animate={isActive ? { scale: [1, 1.05, 1] } : {}}
          transition={{ duration: 1, repeat: Infinity }}
        >
          <Mic
            className={`w-4 h-4 transition-colors duration-300 ${
              isActive ? "text-primary-foreground" : "text-muted-foreground"
            }`}
          />
        </motion.div>
      </div>

      {isSpeaking ? (
        <div className="flex items-center gap-1">
          {[0, 1, 2, 3, 4].map((i) => (
            <motion.span
              key={i}
              className="w-1 bg-primary rounded-full"
              animate={{
                height: [8, 20, 8],
              }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: i * 0.1,
                ease: "easeInOut",
              }}
            />
          ))}
          <span className="text-xs font-medium text-muted-foreground ml-2">
            Speaking
          </span>
        </div>
      ) : (
        <span className="text-xs font-medium text-muted-foreground">
          {isListening ? "Listening..." : "Ready"}
        </span>
      )}
    </div>
  );
}
