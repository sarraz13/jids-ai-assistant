from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ai_service import generate_ai_reply
from .models import ChatSession, Message
from .serializers import MessageSerializer
from .agent_service import run_agent
from django.core.files.storage import default_storage

class AgentView(APIView):
    """
    POST /api/agent/
    Uses the LangChain agent with RAG tool to respond to messages.
    """
    
    def post(self, request):
        user_message = request.data.get("message", "").strip()
        session_id = request.data.get("session_id")
        uploaded_file = request.FILES.get('file')
        
        # Handle file upload if present
        file_content = ""
        if uploaded_file:
            try:
                # Read text files
                if uploaded_file.name.endswith('.txt'):
                    file_content = uploaded_file.read().decode('utf-8')
                    user_message += f"\n\nFile content ({uploaded_file.name}):\n{file_content}"
                elif uploaded_file.name.endswith(('.pdf', '.docx', '.doc')):
                    # You'll need to install libraries for PDF/DOCX processing
                    # For now, just acknowledge the file
                    user_message += f"\n\n[Attached file: {uploaded_file.name} - content processing not yet implemented]"
                else:
                    user_message += f"\n\n[Attached file: {uploaded_file.name}]"
                
                print(f"[AgentView] Processed file: {uploaded_file.name}")
            except Exception as e:
                print(f"[AgentView] Error processing file: {str(e)}")
                user_message += f"\n\n[Error processing file: {uploaded_file.name}]"
        
        if not user_message:
            return Response(
                {"error": "Message is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 1. Get or create session
        if session_id and session_id not in [None, '', 'null', 'undefined']:
            try:
                # Convert to integer if it's a numeric string
                try:
                    session_id_int = int(session_id)
                except ValueError:
                    # If it's not a valid integer, create a new session
                    session = ChatSession.objects.create(title=user_message[:50])
                    print(f"[AgentView] Invalid session_id '{session_id}', created new session: {session.id}")
                else:
                    # Try to get existing session
                    session = ChatSession.objects.get(id=session_id_int)
                    print(f"[AgentView] Using existing session: {session_id_int}")
            except ChatSession.DoesNotExist:
                # Session doesn't exist, create a new one
                session = ChatSession.objects.create(title=user_message[:50])
                print(f"[AgentView] Session {session_id_int} not found, created new: {session.id}")
        else:
            # No session_id provided, create new session
            session = ChatSession.objects.create(title=user_message[:50])
            print(f"[AgentView] Created new session: {session.id}")
        
        # 2. Save user message
        user_msg_obj = Message.objects.create(
            session=session,
            role="user",
            content=user_message
        )
        print(f"[AgentView] Saved user message (ID: {user_msg_obj.id})")
        
        # 3. Build chat history from previous messages (exclude current message)
        all_messages = Message.objects.filter(
            session=session
        ).order_by('created_at')
        
        # Get all messages except the last one (the user message we just created)
        previous_messages = list(all_messages)[:-1] if all_messages.count() > 1 else []
        
        chat_history = []
        temp_user_msg = None
        
        for msg in previous_messages:
            if msg.role == "user":
                temp_user_msg = msg.content
            elif msg.role == "assistant" and temp_user_msg:
                chat_history.append((temp_user_msg, msg.content))
                temp_user_msg = None
        
        print(f"[AgentView] Built chat history with {len(chat_history)} exchanges")
        
        # 4. Run the agent
        try:
            print(f"[AgentView] Calling run_agent...")
            agent_response = run_agent(user_message, chat_history)
            print(f"[AgentView] Agent response received")
        except Exception as e:
            print(f"[AgentView] Error running agent: {str(e)}")
            return Response(
                {"error": f"Agent execution failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 5. Save assistant message
        assistant_msg_obj = Message.objects.create(
            session=session,
            role="assistant",
            content=agent_response
        )
        print(f"[AgentView] Saved assistant message (ID: {assistant_msg_obj.id})")
        
        # 6. Serialize and return
        user_serialized = MessageSerializer(user_msg_obj).data
        assistant_serialized = MessageSerializer(assistant_msg_obj).data
        
        return Response({
            "session_id": session.id,
            "user_message": user_serialized,
            "assistant_message": assistant_serialized
        }, status=status.HTTP_200_OK)
class ChatView(APIView):
    """
    Simple chat endpoint.
    For now it returns a fake AI reply.
    Later, Member 2 will plug LangChain here.
    """

    def post(self, request):
        user_message = request.data.get("message")
        session_id = request.data.get("session_id")

        if not user_message:
            return Response(
                {"error": "Field 'message' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create chat session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                return Response(
                    {"error": "Invalid session_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            session = ChatSession.objects.create()

        # Save user message
        Message.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        assistant_reply = generate_ai_reply(user_message)

        Message.objects.create(
            session=session,
            role='assistant',
            content=assistant_reply
        )

        return Response(
            {
                "session_id": session.id,
                "reply": assistant_reply,
            },
            status=status.HTTP_200_OK
        )
