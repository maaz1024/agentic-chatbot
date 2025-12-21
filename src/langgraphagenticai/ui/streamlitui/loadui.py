import streamlit as st
import os
from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        # 1. Branding & Page Config
        st.set_page_config(
            page_title=self.config.get_page_title(), 
            page_icon="🤖", 
            layout="wide"
        )
        
        st.header(self.config.get_page_title())
        st.markdown(
            """
            **Nexus AI Analyst** | Powered by LangGraph & Llama 3.3
            
            An autonomous agent capable of performing web research, maintaining conversation memory, 
            and generating specialized news reports.
            """
        )

        # Initialize session state for AI News
        if "timeframe" not in st.session_state:
            st.session_state.timeframe = ''
        if "IsFetchButtonClicked" not in st.session_state:
            st.session_state.IsFetchButtonClicked = False
                  
        with st.sidebar:
            st.title("🕹️ Control Panel")
            
            # --- 2. Usecase Selection (Primary User Action) ---
            usecase_options = self.config.get_usecase_options()
            self.user_controls["selected_usecase"] = st.selectbox("Select Agent Mode", usecase_options, index=1)

            # ---------------------------------------------------------
            # State Reset Logic: If the user switches AWAY from 'AI News', reset the fetch button state.
            # ---------------------------------------------------------
            if self.user_controls["selected_usecase"] != "AI News":
                st.session_state.IsFetchButtonClicked = False
                st.session_state.timeframe = ''

            # --- 3. API Key & Model Management ---
            # We try to fetch keys from Secrets (Cloud) or Environment (Local) first
            system_groq_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
            system_tavily_key = st.secrets.get("TAVILY_API_KEY") or os.environ.get("TAVILY_API_KEY")

            # Defaults
            groq_key = system_groq_key
            tavily_key = system_tavily_key
            selected_model = "meta-llama/llama-4-scout-17b-16e-instruct"
            selected_llm = "Groq"

            # Visual Feedback for System Keys
            if system_groq_key:
                st.success("✅ Neural Engine Active (Groq)")
            if system_tavily_key and self.user_controls["selected_usecase"] != "Basic Chatbot":
                st.success("✅ Search Tools Active (Tavily)")

            # --- 4. Advanced Settings (Hidden by default) ---
            with st.expander("⚙️ Advanced Settings / Override Keys"):
                st.caption("Customize models or provide your own API keys.")
                
                # Model Selection
                model_options = self.config.get_groq_model_options()
                selected_model = st.selectbox("Select Model", model_options, index=0)
                # Manual Key Overrides
                user_groq = st.text_input("Groq API Key (Override)", type="password", help="Leave empty to use system key")
                if user_groq:
                    groq_key = user_groq
                
                if self.user_controls["selected_usecase"] != "Basic Chatbot":
                    user_tavily = st.text_input("Tavily API Key (Override)", type="password", help="Leave empty to use system key")
                    if user_tavily:
                        tavily_key = user_tavily

            # --- 5. Validation & Storage ---
            
            # Store keys in session state/env for lower-level modules to access
            if groq_key:
                st.session_state["GROQ_API_KEY"] = groq_key
                os.environ["GROQ_API_KEY"] = groq_key
            if tavily_key:
                st.session_state["TAVILY_API_KEY"] = tavily_key
                os.environ["TAVILY_API_KEY"] = tavily_key

            # Fail gracefully if keys are strictly missing
            if not groq_key:
                st.warning("⚠️ System missing GROQ_API_KEY. Please enter it in Advanced Settings.")
            if (self.user_controls["selected_usecase"] != "Basic Chatbot") and (not tavily_key):
                 st.warning("⚠️ System missing TAVILY_API_KEY. Please enter it in Advanced Settings.")

            # --- 6. AI News Controls ---
            if self.user_controls['selected_usecase'] == "AI News":
                st.subheader("📰 AI News Explorer")
                time_frame = st.selectbox(
                    "📅 Select Time Frame",
                    ["Daily", "Weekly", "Monthly"],
                    index=0
                )
                if st.button("🔍 Fetch Latest AI News", use_container_width=True):
                    st.session_state.IsFetchButtonClicked = True
                    st.session_state.timeframe = time_frame

            # Fill the dictionary expected by main.py
            self.user_controls["selected_llm"] = selected_llm
            self.user_controls["selected_groq_model"] = selected_model
            self.user_controls["GROQ_API_KEY"] = groq_key
            self.user_controls["TAVILY_API_KEY"] = tavily_key

        return self.user_controls