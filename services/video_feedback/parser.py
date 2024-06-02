from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser


class AnalysisOutputParser(BaseModel):
    goods: list[str] = Field(description="list of good things from presentation")
    bads: list[str] = Field(description="list of bad things from presentation")
    corrections: list[str] = Field(description="list of corrections from presentation")
    suggestions: list[str] = Field(description="list of suggestions for improvement")
    feedback: str = Field(description="overall feedback")


analysis_output_parser = PydanticOutputParser(pydantic_object=AnalysisOutputParser)
