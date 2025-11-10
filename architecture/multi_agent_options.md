# Multi-Agent Design Options: Agents as Tools vs Agents as Graph

| Aspect                    | Agents as Tools                                   | Agents as Graph |
|--------|------------------|-----------------                                  |
| **Setup time**            | ✅ Very fast                                      | ❌ More work |
| **Orchestration control** | ❌ Implicit (LLM decides)                         | ✅ Explicit |
| **Error handling**        | Limited (retries via LC AgentExecutor)            | Fine-grained (per node) |
| **Transparency**          | Moderate                                          | High |
| **Scalability**           | Good for 2–3 tools                                | Excellent for larger systems |
| **Demo appeal**           | Looks smart (LLM “thinks”)                        | Looks engineered (clear pipeline) |
| **Best use case**         | Rapid prototyping                                 | Production or structured flow |


Because LangGraph using Agents as Graph is more controllable and allows error handling and retries as the excercise hints, I decided to go with it altough the task could be implemented faster using agents as Tools.