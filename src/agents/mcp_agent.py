import logging
import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# from mcp.provider import Provider  # Updated import


from ..models.agent_state import AgentState


logger = logging.getLogger(__name__)

class MCPAgent:
    """
    Multi Content Processing Agent responsible for:
    1. Retrieving article content from URLs
    2. Summarizing the retrieved content
    """
    
    _instance = None

    @staticmethod
    def get_agent() -> 'MCPAgent':
        """Get singleton instance of MCPAgent."""
        if MCPAgent._instance is None:
            from ..container import AppContainer
            container = AppContainer()
            MCPAgent._instance = container.mcp_agent()
        return MCPAgent._instance
    
    def __init__(self) -> None:
        """Initialize MCP Agent with LLM and workflow graph."""
        self._max_chars = os.getenv("MAX_CHARS", 12000)  # Max chars to process per article #TODO: make configurable
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        
        self._llm = ChatOpenAI(
            model=model,
            temperature=0.3,
            api_key=openai_api_key,
        )
        
        self._tavily_url = os.getenv("TAVILY_URL", "")
        self._session: Optional[ClientSession] = None
        self._graph = self._build_graph()

    async def _retrieve_articles(self, state: AgentState) -> AgentState:
        logger.info("Retrieving article contents via MCP.")
        try:
            async with streamablehttp_client(url=self._tavily_url, headers={}) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
  
            # await self._connect_to_streamable_http_server(self._tavily_url)
                      #TODO: check optimal batching strategy
                    await session.initialize()
                    for article in state.articles:
                        logger.info(f"Retrieving content for URL: {article['link']}")
                        extracted = await session.call_tool(
                            "tavily_extract",
                            {"urls": [article["link"]], "extract_depth": "advanced"}
                        )     
                        #We can do better at cleaning the content but for the sake of this excercise, the LLM will manage :)      
                        article["content"] = extracted.content[0].text
                        # state.articles[article["link"]]["content"] = article["content"]
        except Exception as e:
            logger.error(f"Error retrieving articles content: {str(e)}")
        return state

    async def _summarize_articles(self, state: AgentState) -> AgentState:
        logger.info("Summarizing article contents")        
        try:
            for article in state.articles:
                # Truncate content if too long
                truncated_content = article["content"][:self._max_chars]
                
                messages = [
                    SystemMessage(content="Summarize the following article in 3-4 sentences. Be concise and factual."),
                    HumanMessage(content=truncated_content)
                ]

                # Generate summary asynchronously
                response = await self._llm.ainvoke(messages)
                summary = response.content.strip()

                article["summary"] = summary
                state.summarized_articles.append({
                    "title": article.get("title", "Untitled"),
                    "link": article.get("link", ""),
                    "summary": summary
                })
                
        except Exception as e:
                logger.error(f"Error summarizing content")
                
        return state

    def _build_graph(self) -> StateGraph:
        """Build the workflow graph for content processing."""
        graph = StateGraph(
            state_schema=AgentState,
            name="mcp_workflow")
        
        # Add nodes
        graph.add_node("retrieve", self._retrieve_articles)
        graph.add_node("summarize", self._summarize_articles)
        
        # Set entry point and edges
        graph.set_entry_point("retrieve")
        graph.add_edge("retrieve", "summarize")
        graph.add_edge("summarize", END)
        
        return graph.compile()

    async def ainvoke(self, state: AgentState) -> AgentState:
        """Invoke the MCP workflow graph asynchronously."""
        try:
            return await self._graph.ainvoke(state)
        except Exception as e:
            logger.error(f"Error in MCP workflow: {str(e)}")
            return {}
   