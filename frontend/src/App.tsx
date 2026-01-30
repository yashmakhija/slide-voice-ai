import { useEffect, useRef } from "react";
import { Header } from "@/components/Header";
import { SlideView } from "@/components/SlideView";
import { SlideControls } from "@/components/SlideControls";
import { usePresentationStore } from "@/stores";
import { VoiceSessionProvider } from "@/contexts";

function App() {
  const fetchSlides = usePresentationStore((s) => s.fetchSlides);
  const isLoading = usePresentationStore((s) => s.isLoading);
  const error = usePresentationStore((s) => s.error);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      fetchSlides();
    }
  }, [fetchSlides]);

  return (
    <VoiceSessionProvider>
      <div className="min-h-svh bg-background">
        <Header />

        <main className="flex min-h-svh items-center justify-center pt-20 pb-24">
          {error ? (
            <div className="w-full max-w-2xl mx-auto px-6">
              <div className="rounded-2xl bg-destructive/10 p-8 text-center">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            </div>
          ) : (
            <SlideView isLoading={isLoading} />
          )}
        </main>

        <SlideControls />
      </div>
    </VoiceSessionProvider>
  );
}

export default App;
