# container.py

from dependency_injector import containers, providers

from .agents.manager_agent import ManagerAgent
from .agents.kb_agent import KBAgent
from .agents.mcp_agent import MCPAgent


class AppContainer(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the application.
    """
    # Define Agnets as Singleton.
    manager_agent = providers.Singleton(ManagerAgent)
    kb_agent = providers.Singleton(KBAgent)
    mcp_agent = providers.Singleton(MCPAgent)
