import logging
import os
import textwrap
from typing import List

from langgraph.graph import StateGraph, END 

from ..models.agent_state import AgentState
from .kb_agent import KBAgent
from .mcp_agent import MCPAgent

logger = logging.getLogger(__name__)

class ManagerAgent:
    """
    Orchestrates a user query -> KB lookup -> MCP summarization -> synthesis.
    Singleton pattern via get_agent() method.
    """
  
    _instance = None  # Class variable to store singleton instance

    @staticmethod
    def get_agent() -> 'ManagerAgent':
        """
        Get the singleton instance of ManagerAgent from the container.
        
        Returns:
            ManagerAgent: The singleton instance
        """
        if ManagerAgent._instance is None:
            from ..container import AppContainer
            container = AppContainer()
            ManagerAgent._instance = container.manager_agent()
        return ManagerAgent._instance

    def __init__(
        self,
    ) -> None:
        self._graph: StateGraph = self._build_graph()
        self._max_kb_results = os.getenv("MAX_ARTICLES", 5)
        self._kb_agent: KBAgent = KBAgent.get_agent()
        self._mcp_agent: MCPAgent = MCPAgent.get_agent()
      

    async def _kb_lookup(self, state: AgentState) -> AgentState:
        # This would typically call your actual KB implementation
        try:         
            state.articles = self._kb_agent.search(state.query, self._max_kb_results)
            return state
        except Exception as e:
            logger.error(f"KB lookup failed: {str(e)}")
            return []

    async def _mcp_summarize(self, state: AgentState) -> AgentState:
        logger.info("Starting MCP summarization for retrieved articles.")
        try:
            state =  await self._mcp_agent.ainvoke(state)
            
        except Exception as e:
            logger.error(f"MCP summarization failed: {str(e)}")
        return state

    def _build_graph(self) -> StateGraph:
        graph: StateGraph = StateGraph(
            name="manager_orchestration", 
            state_schema=AgentState    
        )
        
        # Define nodes and edges as needed
        graph.add_node("kb_lookup", self._kb_lookup)
        graph.add_node("mcp_summarize", self._mcp_summarize)

        graph.set_entry_point("kb_lookup")
        graph.add_edge("kb_lookup", "mcp_summarize")
        graph.add_edge("mcp_summarize", END)
        
        return graph.compile()

    async def handle_message(self, message: str) -> List[str]:
        try:
            initial_state: AgentState = AgentState(query=message)
            result: AgentState = await self._graph.ainvoke(initial_state)
            
            summaries_text = "\n\n".join(
                [textwrap.dedent(f"""\
                    Source: {art['link']}
                    Summary:
                    {art['summary']}
                """) for art in result.get("summarized_articles", [])]
            )

            summaries_list: List[str] = []

            for i, art in enumerate(result.get("summarized_articles", []), start=1):
                summary_text = textwrap.dedent(f"""\
                    {i}. Source: {art['link']}
                    Summary:
                    {art['summary']}
                    ====================
                """)
                summaries_list.append(summary_text)

            return summaries_list     
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return ["An error occurred while processing your request."]

        
