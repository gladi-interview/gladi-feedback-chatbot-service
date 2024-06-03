import google.generativeai as genai
import numpy as np

from dependencies.settings import get_settings

settings = get_settings()
genai.configure(api_key=settings.GEMINI_AI_KEY)

def isTranscriptMatch(file_doc, transcript):
    context = ""

    for i in range(len(file_doc)):
        context += file_doc[i].page_content

    content = [
        context,
        transcript
    ]

    result = genai.embed_content(
        model="models/embedding-001",
        content=content,
        task_type="semantic_similarity"
    )

    embedding1 = result['embedding'][0]
    embedding2 = result['embedding'][1]

    similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    return True if (similarity >= 0.75) else False