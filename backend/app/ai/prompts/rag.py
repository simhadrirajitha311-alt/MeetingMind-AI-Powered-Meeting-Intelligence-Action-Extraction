RAG_PROMPT = """
Answer ONLY from the supplied meeting context.
If the answer cannot be found in the context, say: "I couldn't find that information in this meeting."
Never invent information.
Include the relevant source timestamps.

Context:
{context}
Question:
{question}
"""
