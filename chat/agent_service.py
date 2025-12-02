# chat/agent_service.py
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Import RAG service
from .rag_service import search_docs

# -------------------------------------------------------------------
# 1. RAG Tool Function
# -------------------------------------------------------------------

def search_documents_tool(query: str) -> str:
    """
    Wrapper for searching indexed documents.
    Calls search_docs() from rag_service and returns plain text.
    """
    print(f"[TOOL] search_documents called with query: {query}")
    results = search_docs(query, k=4)
    
    if not results:
        return "No relevant document chunks found in the database."
    
    # Join results into readable text
    formatted_results = "\n\n---\n\n".join(results)
    print(f"[TOOL] Found {len(results)} document chunks")
    return formatted_results


# -------------------------------------------------------------------
# 2. LLM Configuration
# -------------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


# -------------------------------------------------------------------
# 3. Simple ReAct Agent Implementation
# -------------------------------------------------------------------

def run_agent(message: str, chat_history):
    """
    Simple ReAct-style agent that uses the search_documents tool.
    
    Args:
        message: The user's current message/question
        chat_history: List of tuples [(user_msg, assistant_msg), ...]
    
    Returns:
        str: The agent's response
    """
    print(f"\n{'='*60}")
    print(f"[AGENT] Processing message: {message}")
    print(f"[AGENT] Chat history length: {len(chat_history)}")
    
    # Format chat history
    formatted_history = ""
    if chat_history:
        for i, (user_msg, assistant_msg) in enumerate(chat_history[-5:], 1):
            formatted_history += f"User: {user_msg}\nAssistant: {assistant_msg}\n\n"
    else:
        formatted_history = "No previous conversation.\n\n"
    
    # System prompt with tool description
    system_prompt = """You are an AI assistant with access to a document search tool.

You can use the following tool:
- search_documents(query): Searches indexed documents for relevant information

When you need to search documents, respond in this EXACT format:
TOOL_CALL: search_documents
QUERY: <your search query here>

After receiving tool results, provide your final answer normally without any special formatting.

Instructions:
1. If the user asks about documents or specific information, use the search_documents tool
2. Base your answer on the document content found
3. If no relevant documents are found, state this clearly
4. Be concise and accurate
"""
    
    max_iterations = 3
    conversation = formatted_history
    
    try:
        for iteration in range(max_iterations):
            print(f"[AGENT] Iteration {iteration + 1}/{max_iterations}")
            
            # Build the prompt
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"{conversation}User: {message}")
            ]
            
            # Get LLM response
            response = llm.invoke(messages)
            agent_response = response.content
            
            print(f"[AGENT] Response: {agent_response[:200]}...")
            
            # Check if agent wants to use a tool
            if "TOOL_CALL:" in agent_response and "search_documents" in agent_response:
                # Extract query
                lines = agent_response.split('\n')
                query = None
                for line in lines:
                    if line.startswith("QUERY:"):
                        query = line.replace("QUERY:", "").strip()
                        break
                
                if query:
                    print(f"[AGENT] Tool call detected: search_documents('{query}')")
                    
                    # Execute tool
                    tool_result = search_documents_tool(query)
                    
                    # Add to conversation
                    conversation += f"User: {message}\n"
                    conversation += f"Assistant (thinking): I'll search for: {query}\n"
                    conversation += f"Tool Result:\n{tool_result}\n\n"
                    
                    # Update message to ask for final answer
                    message = "Based on the search results above, please provide your final answer to the user's question."
                    
                else:
                    # Malformed tool call, return what we have
                    print("[AGENT] Malformed tool call, returning response")
                    return agent_response
            else:
                # No tool call, this is the final answer
                print("[AGENT] Final answer generated")
                print(f"{'='*60}\n")
                return agent_response
        
        # Max iterations reached
        print("[AGENT] Max iterations reached")
        print(f"{'='*60}\n")
        return agent_response
    
    except Exception as e:
        error_msg = f"Agent error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"{'='*60}\n")
        return f"I encountered an error while processing your request: {str(e)}"