# Tavily API Methods – Comparison for MCP Agent

| **Method** | **Purpose** | **Typical Input** | **Output** | **Relevance for Assignment** | **Recommended Usage** |
|-------------|--------------|-------------------|-------------|-------------------------------|-----------------------|
| `search` | Executes a natural language query (e.g., "AI trends 2025") and returns relevant URLs, short snippets, and optionally a synthesized answer. | `query: str` + optional params (`search_depth`, `max_results`, etc.) | List of sources with `title`, `url`, `content`, `score` | 🟡 *Optional* — use if the Manager Agent needs to discover new articles dynamically. | Use only if you want your MCP to find related content when the KB doesn’t have a direct match. |
| `extract` | Fetches and cleans the full content of one or more URLs. | `urls: list[str]`, `format: "text"` or `"markdown"`, `extract_depth` | Cleaned full text content per URL | 🟢 *Essential* — this is required to fetch and summarize the article. | Use to retrieve and prepare article text for summarization. |
| `crawl` | Recursively follows links and extracts multiple pages from a site. | `url`, optional `depth` or config params | Multiple pages’ extracted content | 🔴 *Overkill* — not needed for single-article summarization. | Skip for this assignment. Useful only for broader site exploration. |
| `map` | Extracts structured data (tables, key facts, fields) from page content. | URL(s) + extraction pattern or config | Structured JSON data | ⚪ *Optional* — helpful for structured metadata extraction. | Optional future enhancement (e.g., extract title, author, tags automatically). |

---

Since I'm not familiar with Tavily, I decided to go with extract that seems to return full content of a url which I will process myself