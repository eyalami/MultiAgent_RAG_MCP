from dataclasses import dataclass, field
from typing import Any, List, Dict

@dataclass
class AgentState:
    """Graph state passed between agents."""
    query: str = ""
    articles: List[Dict[str, Any]] = field(default_factory=list)
    summarized_articles: List[Dict[str, Any]] = field(default_factory=list)
    answer: str = ""