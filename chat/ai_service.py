from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .rag_service import search_docs

# Prepare model once (not on every request)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Improved prompt with better context usage
prompt_template = """
You are a helpful assistant. Use the context below to answer the question. 
The context comes from trusted documents.

CONTEXT:
{context}

QUESTION: {message}

INSTRUCTIONS:
- Use the context above to answer the question
- If the context provides relevant information, use it in your answer
- If the context doesn't fully answer the question, use your general knowledge
- Be helpful and provide a complete answer
- Keep your response concise and informative

ANSWER:
"""

prompt = PromptTemplate.from_template(prompt_template)
parser = StrOutputParser()

chain = prompt | model | parser

def generate_ai_reply(user_message: str) -> str:
    """
    Enhanced with RAG - searches documents before generating response
    """
    print(f"🔍 USER QUESTION: '{user_message}'")
    
    # Search for relevant document chunks
    relevant_chunks = search_docs(user_message, k=3)
    
    # Build context from chunks
    if relevant_chunks:
        context_text = "\n\n".join(relevant_chunks)
        print("🎯 RAG CONTEXT FOUND!")
        print(f"📊 Chunks retrieved: {len(relevant_chunks)}")
        print(f"📝 First chunk preview: {relevant_chunks[0][:200]}...")
    else:
        context_text = "No specific context available."
        print("❌ NO RAG CONTEXT FOUND")
    
    # Generate response with context
    response = chain.invoke({
        "context": context_text, 
        "message": user_message
    })
    
    print(f"🤖 AI RESPONSE: {response[:200]}...")
    print("---" * 20)
    return response