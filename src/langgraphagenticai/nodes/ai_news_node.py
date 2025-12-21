from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os

class AINewsNode:
    def __init__(self, llm):
        """
        Initialize the AINewsNode with API keys for Tavily and GROQ.
        """
        self.tavily = TavilyClient()
        self.llm = llm
        self.state = {}

    def fetch_news(self, state: dict) -> dict:
        """
        Fetch AI news based on the specified frequency.
        """
        frequency = state['messages'][0].content.lower()
        self.state['frequency'] = frequency
        
        time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}

        # Safety check for invalid frequency defaults
        if frequency not in time_range_map:
            frequency = 'daily'

        response = self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news globally",
            topic="news",
            time_range=time_range_map.get(frequency, 'd'),
            include_answer="advanced",
            max_results=20,
            days=days_map.get(frequency, 1)
        )

        state['news_data'] = response.get('results', [])
        self.state['news_data'] = state['news_data']
        return state
    

    def summarize_news(self, state: dict) -> dict:
        """
        Summarize the fetched news using an LLM.
        """
        news_items = self.state.get('news_data', [])

        # Graceful handling if no news is found
        if not news_items:
            self.state['summary'] = "No news found for the selected period."
            return self.state

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical news analyst. 
            Your goal is to summarize the provided list of AI news articles into a professional Markdown report.

            STRICT FORMATTING RULES:
            1. **Grouping**: Group all articles strictly by their Date. Do not repeat date headers.
            2. **Date Header**: Use `### MM-DD-YYYY` format for the date headers.
            3. **Sorting**: Sort dates descending (newest dates at the top).
            4. **Item Format**: For each article, use exactly this bullet point format:
               * **[Source Name]** – [Concise Summary]. [link](URL)
            5. **Links**: Never output the raw URL. Always wrap it in the text `[link]`.
            6. **Source Name**: Extract the publisher name from the URL or content (e.g., 'TechCrunch', 'Reuters').

            EXAMPLE OUTPUT:
            ### 12-20-2025
            * **TechCrunch** – AI startups showing resilience in new market trends. [link](https://techcrunch.com/...)
            * **Reuters** – Global data center demand hits record high. [link](https://reuters.com/...)

            ### 12-19-2025
            * **Wired** – New benchmarks released for LLM reasoning. [link](https://wired.com/...)
            """),
            ("user", "Here are the articles to summarize:\n{articles}")
        ])

        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
            for item in news_items
        ])

        response = self.llm.invoke(prompt_template.format(articles=articles_str))
        state['summary'] = response.content
        self.state['summary'] = state['summary']
        return self.state
    
    def save_result(self, state):
        """
        Saves the summary to a markdown file with UTF-8 encoding.
        """
        frequency = self.state.get('frequency', 'daily')
        summary = self.state.get('summary', 'No summary generated.')
        
        if not os.path.exists("./AINews"):
            os.makedirs("./AINews")

        filename = f"./AINews/{frequency}_summary.md"
    
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
            
        self.state['filename'] = filename
        return self.state