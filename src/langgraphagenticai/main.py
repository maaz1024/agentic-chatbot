import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMs.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit

def render_welcome_message(usecase):
    """
    Displays a contextual welcome message based on the selected use case.
    """
    if usecase == "Basic Chatbot":
        with st.container(border=True):
            st.markdown("### 💬 Basic Chatbot")
            st.info(
                """
                **Functionality:**
                - A pure LLM conversational agent.
                - Maintains conversation history (Stateful).
                
                **Limitations:**
                - ❌ No internet access.
                - ❌ Knowledge cutoff applies (cannot answer current events).
                
                **Try asking:** *"Explain Quantum Computing to a 5-year-old."*
                """
            )
            
    elif usecase == "Chatbot With Web":
        with st.container(border=True):
            st.markdown("### 🌐 Chatbot with Web Search")
            st.info(
                """
                **Functionality:**
                - An agentic chatbot connected to **Tavily Search**.
                - Can browse the live web to find real-time information.
                - Cites sources for its answers.
                
                **Limitations:**
                - ⏳ Slightly slower (needs time to search & read).
                
                **Try asking:** *"Who won the latest F1 race?"* or *"Stock price of Nvidia today."*
                """
            )

    elif usecase == "AI News":
        with st.container(border=True):
            st.markdown("### 📰 AI News Analyst")
            st.info(
                """
                **Functionality:**
                - A fully autonomous workflow.
                - Fetches top AI news, summarizes it, and generates a markdown report.
                - Saves the report locally for download.
                
                **How to use:**
                - Select a timeframe (Daily/Weekly) from the sidebar and click **Fetch News**.
                """
            )

def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    """
    # Load UI
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()
    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return
    
    # Check if keys are present (Security Check)
    if not user_input.get("GROQ_API_KEY"):
        st.stop()
    if user_input.get("selected_usecase") != "Basic Chatbot" and not user_input.get("TAVILY_API_KEY"):
        st.stop()

    usecase = user_input.get("selected_usecase")

    # -------------------------------------------------------------
    # DETECT MODE SWITCH & CLEAR HISTORY
    # -------------------------------------------------------------
    # 1. Initialize the tracker if it doesn't exist
    if "last_usecase" not in st.session_state:
        st.session_state.last_usecase = usecase
    # 2. Check if the user changed modes
    if st.session_state.last_usecase != usecase:
        st.session_state.chat_history = []  # Wipe the memory
        st.session_state.last_usecase = usecase  # Update the tracker
        # Optional: Rerun to refresh the UI immediately (clears old chat visually)
        st.rerun()

    # -------------------------------------------------------------
    # 1. SESSION STATE SETUP (Memory)
    # -------------------------------------------------------------
    # We maintain a separate history list for the UI
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # -------------------------------------------------------------
    # 2. RENDER HISTORY
    # -------------------------------------------------------------
    # Only render history for Chatbot modes, not AI News (which is a report)
    if usecase != "AI News":
        # Draw all previous messages
        for message in st.session_state.chat_history:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)

    # -------------------------------------------------------------
    # 3. HANDLE INPUT
    # -------------------------------------------------------------
    user_message = None
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe 
    else:
        placeholder_text = "Ask me anything..."
        if usecase == "Chatbot With Web":
            placeholder_text = "Ex: Who won the latest F1 race?"
        user_message = st.chat_input(placeholder_text)

    # -------------------------------------------------------------
    # 4. EXECUTION LOGIC
    # -------------------------------------------------------------
    if user_message:
        # A. Display the NEW user message immediately
        if usecase != "AI News":
            with st.chat_message("user"):
                st.write(user_message)
            # Add to history
            st.session_state.chat_history.append(HumanMessage(content=user_message))

        try:
            # B. Configure LLM & Graph
            obj_llm_config = GroqLLM(user_contols_input=user_input)
            model = obj_llm_config.get_llm_model()

            if not model:
                st.error("Error: LLM model could not be initialized")
                return
            
            graph_builder = GraphBuilder(model)
            graph = graph_builder.setup_graph(usecase)
            
            # C. Run Graph
            # For Basic Chatbot, we pass the FULL history. For AI News, we just pass the timeframe string.
            if usecase == "Basic Chatbot":
                graph_input = {"messages": st.session_state.chat_history}
            elif usecase == "Chatbot With Web":
                graph_input = {"messages": st.session_state.chat_history}
            else:
                graph_input = {"messages": [HumanMessage(content=user_message)]}

            # D. Display Result & Capture Response            
            with st.chat_message("assistant") if usecase != "AI News" else st.container():
                response_container = st.empty()
                
                # We use your Display Helper, but we rely on it to WRITE to the container
                # Note: This runs the graph inside the helper
                display_obj = DisplayResultStreamlit(usecase, graph, user_message)
                
                # To ensure we capture the output for history, we run graph.invoke HERE instead of inside the display class, 
                if usecase == "AI News":
                     display_obj.display_result_on_ui() # News handles itself
                else:
                    # Chatbot Logic
                    with st.spinner("Thinking..."):
                        response = graph.invoke(graph_input)
                        ai_msg = response["messages"][-1]
                        
                        # Display
                        response_container.write(ai_msg.content)
                        
                        # Save to History
                        st.session_state.chat_history.append(ai_msg)

        except Exception as e:
             st.error(f"Error: {e}")
             
    elif not st.session_state.chat_history and not st.session_state.IsFetchButtonClicked:
        # Show welcome message ONLY if history is empty
        render_welcome_message(usecase)