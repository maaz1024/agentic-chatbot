# 🤖 Nexus AI Analyst

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/maaz1024/nexus-ai-analyst)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful%20Agents-orange)](https://langchain-ai.github.io/langgraph/)
[![Llama 3.3](https://img.shields.io/badge/Model-Llama%203.3%20(Groq)-purple)](https://groq.com/)

**Nexus AI Analyst** is an autonomous multi-agent workspace designed to bridge the gap between static LLMs and real-time internet research. Built on **LangGraph**, it moves beyond simple RAG chains to implement true **agentic workflows** with cyclic decision-making and state persistence.

---

## 🚀 Features & Architecture

### 1. 🧠 Contextual Chat Assistant
**The Feature:** A high-speed conversational agent that remembers context across multiple turns. Unlike standard stateless API calls, this assistant maintains a continuous thread of conversation.

**The Architecture (Stateful Linear):**
The system uses a simple `StateGraph` where the application state (messages) flows linearly. The `Chatbot` node processes input and appends the response to the persistent state, ensuring no context is lost.

![Basic Chatbot Workflow](assets/workflow_basic_chatbot.png)

### 2. 🌐 Autonomous Web Researcher
**The Feature:** An intelligent agent that can browse the live web to answer questions about current events (e.g., Sports, Stock Prices). It cites its sources and can self-correct if initial search results are insufficient.

**The Architecture (Cyclic ReAct Pattern):**
This utilizes a **Cyclic Graph**. The `Chatbot` node acts as a reasoning engine. It decides whether to route to the `Tools` node (Tavily Search) or end the conversation. If it chooses to search, the results are fed back into the loop, allowing the LLM to "reason" over the new data before answering.

![Web Agent Workflow](assets/workflow_chatbot_with_web.png)

### 3. 📰 Automated AI News Analyst
**The Feature:** A fully automated reporting pipeline that fetches global AI news for a specific timeframe (Daily/Weekly), synthesizes it into a structured summary, and generates a downloadable Markdown report.

**The Architecture (Sequential Pipeline):**
A deterministic **ETL (Extract, Transform, Load)** pipeline. The graph executes a strict sequence:
1.  **Fetch Node:** Calls external APIs to get raw articles.
2.  **Summarize Node:** Uses Llama 3.3 to format and condense the data.
3.  **Save Node:** Writes the final output to the local file system.

![AI News Workflow](assets/workflow_ai_news.png)

---

## 📸 Application Screenshots

### 1. Professional Landing & Control Panel
![Landing Page](assets/1_landing_page_basic_chat.png)

### 2. Agentic Reasoning (Real-Time Search)
![Reasoning Engine](assets/2_web_agent_reasoning_sports.png)

### 3. Automated Weekly News Report
![News Report](assets/3_ai_news_weekly_report.png)

### 4. Stateful Memory Persistence
![Memory Test](assets/4_stateful_memory_test.png)

---

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/maaz1024/agentic-chatbot.git](https://github.com/maaz1024/agentic-chatbot.git)
    cd agentic-chatbot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Credentials**
    Create a `.streamlit/secrets.toml` file in the root directory:
    ```toml
    GROQ_API_KEY = "gsk_..."
    TAVILY_API_KEY = "tvly-..."
    ```

4.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure

```text
├── .streamlit/             # Streamlit configuration and secrets
├── assets/                 # Project screenshots and diagrams
├── src/
│   ├── langgraphagenticai/
│   │   ├── graph/          # Graph construction logic (Builder pattern)
│   │   ├── LLMs/           # LLM configuration (Groq)
│   │   ├── nodes/          # Functional units (Chatbot, Search, News)
│   │   ├── state/          # State definition (TypedDict)
│   │   ├── tools/          # External tool definitions (Tavily)
│   │   └── ui/             # Streamlit UI components
│   └── main.py             # Main application logic
├── venv/                   # Virtual environment
├── .gitignore              # Git ignore file
├── app.py                  # Entry point
├── README.md               # Documentation
├── requirements.txt        # Dependencies