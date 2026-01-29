from app.models.slide import Slide

SLIDES: list[Slide] = [
    Slide(
        id=1,
        title="What is Machine Learning?",
        content=[
            "A subset of Artificial Intelligence",
            "Systems that learn from data patterns",
            "Improves performance without explicit programming",
            "Powers recommendations, search, and predictions",
        ],
        narration="""Welcome to this introduction to Machine Learning!

Machine Learning, or ML, is a fascinating subset of Artificial Intelligence.
Unlike traditional programming where we write explicit rules,
ML systems learn patterns directly from data.

The key idea is that these systems improve their performance over time
without being explicitly programmed for each scenario.
You encounter ML every day - from Netflix recommendations
to Google search results to spam filters in your email.""",
    ),
    Slide(
        id=2,
        title="Types of Machine Learning",
        content=[
            "Supervised Learning: Learn from labeled examples",
            "Unsupervised Learning: Find hidden patterns",
            "Reinforcement Learning: Learn through rewards",
        ],
        narration="""There are three main types of Machine Learning.

First, Supervised Learning - this is where we train models using labeled data.
For example, showing the model thousands of images labeled as 'cat' or 'dog'
so it can learn to classify new images.

Second, Unsupervised Learning - here the model finds hidden patterns
in data without any labels. This is great for customer segmentation
or anomaly detection.

Third, Reinforcement Learning - the model learns by taking actions
and receiving rewards or penalties. This powers game-playing AI
and robotics applications.""",
    ),
    Slide(
        id=3,
        title="Real-World Applications",
        content=[
            "Netflix & Spotify: Personalized recommendations",
            "Banks: Fraud detection in real-time",
            "Healthcare: Disease diagnosis from medical images",
            "Tesla: Self-driving car perception",
            "ChatGPT: Natural language understanding",
        ],
        narration="""Machine Learning is everywhere in our daily lives!

Netflix and Spotify use ML to recommend content you'll love.
Banks use it to detect fraudulent transactions in milliseconds.

In healthcare, ML models can analyze medical images to help diagnose diseases.
Companies like Tesla use ML for self-driving car perception systems.

And of course, large language models like the one powering this presentation
use ML to understand and generate human language.""",
    ),
    Slide(
        id=4,
        title="How Models Learn",
        content=[
            "Step 1: Collect and prepare training data",
            "Step 2: Choose a model architecture",
            "Step 3: Train the model on data",
            "Step 4: Evaluate performance on test data",
            "Step 5: Deploy and monitor in production",
        ],
        narration="""Let me walk you through how machine learning models actually learn.

First, we collect and prepare training data - this is often the hardest part.
Quality data is essential for good models.

Next, we choose a model architecture - maybe a neural network,
decision tree, or something else depending on the problem.

Then we train the model, which means showing it the data
and letting it adjust its internal parameters to minimize errors.

After training, we evaluate on test data the model hasn't seen before
to make sure it generalizes well.

Finally, we deploy to production and continuously monitor performance.""",
    ),
    Slide(
        id=5,
        title="Getting Started with ML",
        content=[
            "Python: The language of ML",
            "scikit-learn: Great for beginners",
            "TensorFlow & PyTorch: Deep learning frameworks",
            "Kaggle: Practice with real datasets",
            "Start small: Begin with simple projects",
        ],
        narration="""Ready to start your machine learning journey? Here's how!

Python is the go-to language for ML - it's beginner-friendly
and has amazing libraries.

Start with scikit-learn for classical ML algorithms.
It's perfect for beginners with excellent documentation.

When you're ready for deep learning, explore TensorFlow or PyTorch.
Both are powerful frameworks used in industry and research.

Kaggle is a great platform to practice with real datasets
and learn from the community.

My advice: start small! Build a simple project like a spam classifier
or house price predictor before tackling complex problems.""",
    ),
]


def get_slide_by_id(slide_id: int) -> Slide | None:
    for slide in SLIDES:
        if slide.id == slide_id:
            return slide
    return None


def get_slide_summaries() -> str:
    summaries = []
    for slide in SLIDES:
        summaries.append(f"Slide {slide.id}: {slide.title}")
    return "\n".join(summaries)


def get_total_slides() -> int:
    return len(SLIDES)
