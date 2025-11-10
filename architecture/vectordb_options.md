## 🧩 FAISS vs External Vector Database

| Aspect | **FAISS Local (in-memory/on-disk)** | **Vector DB Container (e.g. Qdrant / Weaviate / Milvus)** |
|--------|-------------------------------------|------------------------------------------------------------|
| **Setup time** | ✅ Instant (no extra container) | ❌ Requires setup and configuration |
| **Performance** | ⚡ Very fast (no network overhead) | Slightly slower (HTTP/gRPC round-trips) |
| **Scalability** | Limited to single-node usage | ✅ Horizontally scalable and distributed |
| **Ease of use** | Simple — load and query index from file | Requires API client integration |
| **Dynamic updates** | ❌ Index must be rebuilt for updates | ✅ Supports real-time insert/delete |
| **Persistence** | File-based (easy to persist with Docker volume) | Persistent via database storage |
| **Features** | Basic semantic search only | ✅ Advanced: metadata filters, hybrid search, multi-tenancy |
| **Maintenance** | Minimal | Requires DB monitoring and versioning |
| **Production readiness** | Good for small apps and demos | ✅ Excellent for enterprise / scalable deployments |
| **Best use case** | Lightweight local RAG / prototyping | Large-scale or dynamic RAG pipelines |
| **Assignment suitability** | ✅ Perfect (simple, local, fast) | Overkill for current scope |

I would use a container with a dedicated Vector DB for a real case scenario but since the excercise requirement clearly stated a local FAISS vector store I followed instructions and decided to keep it simple


about the embeddings and preprocessing:

Since the dataset didn't contain the content, each document was relatively small
Moreover, the entire corpus was small-medium (less than 100k)
Considering the excercise, i assumed searches would be free text so ranking of relevant fields by importance are:
1. title 2. subtitle 3. link 4. author 5. date

For the above reasons + simplicity I decided to embed each docuement separately (no chunking) and use relatively small model with good latency/accuracy balance, I decided to use local model for cost vs. processing resources/time. 
Preprocessing is minimal and related to fields rank.  