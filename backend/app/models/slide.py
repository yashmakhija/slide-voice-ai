from pydantic import BaseModel, Field


class Slide(BaseModel):

    id: int = Field(..., ge=1, description="Unique slide identifier (1-indexed)")
    title: str = Field(..., min_length=1, description="Slide title")
    content: list[str] = Field(
        default_factory=list, description="Bullet points for the slide"
    )
    narration: str = Field(..., min_length=1, description="AI narration script")


class SlideNavigationRequest(BaseModel):

    slide_id: int = Field(..., ge=1, description="Target slide ID")
    reason: str | None = Field(None, description="Why navigating to this slide")


class CurrentSlideResponse(BaseModel):

    slide: Slide
    total_slides: int = Field(..., ge=1, description="Total number of slides")
    has_next: bool = Field(..., description="Whether there's a next slide")
    has_previous: bool = Field(..., description="Whether there's a previous slide")
