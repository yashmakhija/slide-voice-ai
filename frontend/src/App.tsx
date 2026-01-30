import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function App() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-foreground">
            AI Voice Presentation
          </h1>
          <p className="mt-2 text-muted-foreground">
            Interactive voice-controlled ML presentation
          </p>
        </header>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Slide 1: What is Machine Learning?</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-2 pl-6">
              <li>A subset of Artificial Intelligence</li>
              <li>Systems that learn from data patterns</li>
              <li>Improves performance without explicit programming</li>
            </ul>
          </CardContent>
        </Card>

        <div className="flex justify-center gap-4">
          <Button variant="outline">Previous</Button>
          <Button>Start Presentation</Button>
          <Button variant="outline">Next</Button>
        </div>
      </div>
    </div>
  );
}

export default App;
