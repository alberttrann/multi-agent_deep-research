# Multi-Agent Research System (MCP)

A powerful research assistant system that leverages multiple AI agents to conduct comprehensive technical research and generate detailed reports. The system combines web search capabilities with advanced language models to create well-structured, thoroughly-researched content.

## Features

- **Multi-Agent Architecture**
  - OrchestratorAgent for high-level research planning and progress evaluation
  - PlannerAgent for creating targeted search strategies
  - ReportAgent for synthesizing findings into coherent reports

- **Flexible LLM Support**
  - Google's Gemini API integration
  - OpenRouter API support for various models (Claude 3, etc.)
  - Easy switching between providers

- **Advanced Search Capabilities**
  - Integration with Tavily API for high-quality source gathering
  - Intelligent deduplication and relevance filtering
  - Depth-based content evaluation

- **Smart Research Planning**
  - Dynamic research strategies based on content depth
  - Automatic progress evaluation
  - Prioritized information gathering

- **Rich Reporting**
  - Well-structured markdown output
  - Proper source citation
  - Code examples with language tags
  - Technical accuracy focus

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp.git
cd mcp

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

Create a .env file in the project root:

```env
OPENROUTER_API_KEY="your-openrouter-key"
TAVILY_API_KEY="your-tavily-key"
YOUR_SITE_URL="http://localhost:7860"  # Optional: For OpenRouter ranking headers
YOUR_SITE_NAME="My Multi-Agent RAG MCP Server"  # Optional
```

## Required API Keys

| Provider | Required | Purpose | Get Key |
|----------|----------|----------|----------|
| Tavily | Yes | Web search | [Tavily API](https://tavily.com) |
| Gemini | Optional* | LLM provider | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| OpenRouter | Optional* | LLM provider | [OpenRouter](https://openrouter.ai/keys) |

\* At least one LLM provider (either Gemini or OpenRouter) is required

## Usage

### Web Interface

```bash
python mcp_server.py
```

Then open your browser to `http://localhost:7860`

## Architecture

### Components

#### OrchestratorAgent
- Creates comprehensive research plans
- Evaluates research progress
- Ensures thorough topic coverage

#### PlannerAgent
- Generates targeted search strategies
- Prioritizes research needs
- Ensures investigation depth

#### ReportAgent
- Synthesizes research findings
- Generates structured reports
- Maintains technical accuracy

#### MultiAgentSystem
- Coordinates agent interactions
- Manages research workflow
- Handles API integrations

## Configuration

### Supported Models

#### Gemini Models
- gemini-2.0-flash
- gemini-2.0-flash-lite
- gemini-1.5-pro
- gemini-2.5-pro-preview-05-06
- gemini-2.5-flash-preview-04-17

#### OpenRouter Models
- Any valid OpenRouter model ID (e.g., "anthropic/claude-3-opus:beta")

### System Parameters

```python
MAX_SEARCHES_TOTAL = 30    # Maximum number of web searches
MIN_RESULTS_PER_ITEM = 3   # Minimum results before progress check
MAX_ATTEMPTS_PER_ITEM = 2  # Maximum research attempts per item
```

## Output Format

The system generates markdown-formatted reports including:
- Comprehensive introduction
- Technical analysis sections
- Code examples with language tags
- Comparative analysis
- Implementation considerations
- Properly cited sources

## Logging

Logs are stored in the logs directory with:
- Daily rotation
- Debug level for file logging
- Info level for console output
- Structured format for easy parsing

## Development

### Project Structure

```
mcp/
├── agents.py           # Agent implementations
├── mcp_server.py      # Web interface server
├── mcp_client.py      # CLI client
├── utils.py           # Utility functions
├── logger_config.py   # Logging configuration
├── requirements.txt   # Dependencies
└── .env              # Environment variables
```

### Adding New Features

1. Agent Modifications:
   - Extend BaseAgent class
   - Implement required methods
   - Add to MultiAgentSystem

2. Custom Search Sources:
   - Implement in MultiAgentSystem.web_search()
   - Add appropriate API configurations

3. UI Enhancements:
   - Modify create_interface() in mcp_server.py
   - Update CSS in css variable

## Support

For questions and support:
- Open an issue in the GitHub repository
- Detailed bug reports should include logs and steps to reproduce

## Acknowledgments

- [Gradio](https://www.gradio.app/) for the web interface
- [Tavily](https://tavily.com/) for web search capabilities
- [Google Gemini](https://makersuite.google.com/) for language model support
- [OpenRouter](https://openrouter.ai/) for additional model access

## Future Features
- MCP implementation
- CLI-based UI

## Snapshots

![Screenshot 2025-06-07 230054](https://github.com/user-attachments/assets/763a6e3c-ac1b-4771-804a-d0945b9e652e)

![Screenshot 2025-06-07 230038](https://github.com/user-attachments/assets/8979acf8-1e1e-44a0-b9a2-a1f920dcea7c)

![Screenshot 2025-06-07 230539](https://github.com/user-attachments/assets/3d29be53-b007-4bc8-8c6e-eed31e77f8da)

FULL REPORT:
## Production-Grade Search Algorithms: A Technical Analysis of Modern Indexing Systems

### Introduction

Search algorithms form the backbone of production systems, enabling efficient data retrieval across databases, search engines, and distributed applications. This report synthesizes research on indexing structures (B-trees, LSM-trees, hash indexing), modern alternatives (ART, vector indexes), and their real-world performance trade-offs. Analysis focuses on scalability, consistency, latency, and hardware alignment, drawing from benchmarks and architectural studies.

---

### 1. Core Indexing Structures: Trade-offs and Evolution

#### 1.1 B-trees: The Persistent Workhorse

*   **Design**: Self-balancing trees storing sorted data for logarithmic-time operations. Optimized for read-heavy workloads via wide branching (exploiting memory hierarchy) and buffer-pool caching.
*   **Production Use**: Dominates relational databases (e.g., PostgreSQL) due to strong consistency and range-query support.
*   **Trade-offs**:
    *   *Writes*: Random I/O overhead during updates causes write amplification.
    *   *Scalability*: Shard resizing is inflexible (cannot expand post-creation without `shrink` APIs).
*   **Modern Optimizations**: Cache-aware layouts (e.g., CPU cache alignment) and separator-key optimizations to minimize disk seeks.

#### 1.2 LSM-trees: Write-Optimized Log Structuring

*   **Design**: Buffers writes in memory (`memtable`), flushes to disk as immutable SSTables. Background compaction merges files.
*   **Production Use**: Powers NoSQL systems (Cassandra, RocksDB) and full-text search (Lucene).
*   **Trade-offs**:
    *   *Reads*: Higher latency due to multi-SSTable probing.
    *   *Writes*: 2.1× higher throughput than B-trees (USENIX benchmarks) via sequential I/O.
    *   *Space Efficiency*: SSTable blocks are 100% fillable and compressible.
*   **Scalability**: Excels at large-scale ingestion but struggles with real-time consistency.

#### 1.3 Hash Indexing: O(1) Lookup for Point Queries

*   **Design**: Direct key-address mapping via hash functions.
*   **Production Use**: Ideal for caching (Redis), session stores, and real-time lookups.
*   **Limitations**:
    *   No range-query support.
    *   Scalability challenges in distributed systems (outperformed by B-trees for large datasets).

---

### 2. Modern Search Algorithms: Beyond Traditional Trees

#### 2.1 Memory-Efficient Tries (ART/HOT)

*   **Adaptive Radix Trees (ART)**:
    *   3× faster than B-trees on modern hardware by compressing nodes.
    *   Used in analytical databases for low-latency in-memory indexing.
*   **HOT (Height-Optimized Tries)**:
    *   Reduces pointer chasing via SIMD-optimized node layouts.

#### 2.2 Vector Indexing for High-Dimensional Data

*   **Techniques**:
    *   **HNSW (Hierarchical Navigable Small World)**: Approximate nearest-neighbor search with logarithmic scaling.
    *   **IVF (Inverted File)**: Partitions vectors into clusters for coarse-to-fine search.
*   **Trade-offs**:
    *   *Accuracy vs. Speed*: HNSW prioritizes recall; IVF sacrifices precision for throughput.
    *   *Memory vs. Disk*: Hybrid indexes (e.g., disk-based MSTG) enable >RAM scalability.
*   **Use Cases**: AI/ML pipelines (RAG systems), similarity search.

---

### 3. Performance Benchmarks: Real-World Insights

#### 3.1 Search Engine Showdown (Wikipedia Dataset)

| **System**    | Indexing Time (s) | Throughput (ops/sec) | Latency (ms) |
| :------------ | :---------------- | :------------------- | :----------- |
| RediSearch    | 221               | 12,500               | 8            |
| Elasticsearch | 349               | 3,100                | 10           |
| Meilisearch   | 42 (async)        | 150,284              | 6.73         |

*   **RediSearch**: 4× faster queries than Elasticsearch but 2× slower indexing in conflicting benchmarks (Gigasearch).
*   **Meilisearch**: Dominates indexing (7× faster) via asynchronous writes.

#### 3.2 Query-Type Variability

*   **B-trees**: Excel at boolean and range queries (e.g., Elasticsearch: 540 req/sec).
*   **Hash/Vector Indexes**: Crush exact matches (RediSearch: 0.64 ms for phrase queries).
*   **Failure Modes**: Typesense took 224 ms for 3-word queries due to algorithmic bottlenecks.

---

### 4. Distributed Systems Challenges

#### 4.1 Consistency-Latency Trade-offs

*   **Strong Consistency**:
    *   Required for financial systems; increases latency via quorum operations (e.g., `W + R > N` in distributed B-trees).
*   **Eventual Consistency**:
    *   Used in LSM-based NRT (Near Real-Time) systems (e.g., Elasticsearch). Data propagates in seconds, risking transient stale reads.

#### 4.2 Throughput vs. Latency

*   **Indexing Workloads**:
    *   Batch processing (LSM-trees) maximizes throughput but adds seconds/minutes of latency.
    *   Real-time systems (hash indexes) prioritize low-latency writes at throughput costs.
*   **Hardware Constraints**:
    *   Memory-bound systems (Redis) hit scalability walls; disk-spill designs (MSTG) trade speed for capacity.

---

### 5. Future Directions

1.  **Hardware-Aware Indexes**: Leveraging SIMD, NUMA, and persistent memory.
2.  **ML-Driven Optimization**: Adaptive indexing based on query patterns.
3.  **Consistency Automation**: Tunable CAP parameters for dynamic workloads.
4.  **Vector-Hybrid Systems**: Combining HNSW with B-trees for multi-modal queries.

### Conclusion

Production search algorithms require context-aware selection:

*   **B-trees** remain unmatched for consistent, range-heavy workloads.
*   **LSM-trees** dominate write-intensive scenarios but demand compaction tuning.
*   **Vector/Hash indexes** excel in niche domains (AI, caching) but struggle with generalization.
Benchmarks reveal no universal "winner"—throughput, latency, and consistency form an iron triangle. Future innovations must balance algorithmic advances with hardware evolution and distributed systems pragmatism.

## Sources Cited

### Research Papers

1.  [Scalability and Maintainability Challenges and Solutions in Machine ...](https://arxiv.org/html/2504.11079v1)
2.  [Towards Understanding Systems Trade-offs in Retrieval-Augmented ...](https://arxiv.org/html/2412.11854v1)

### Technical Articles & Resources

1.  [Modern B Tree Techniques 1 | PDF | Database Index - Scribd](https://www.scribd.com/document/76382374/Modern-B-Tree-Techniques-1)
2.  [Memory-Efficient Search Trees for Database Management Systems](https://people.iiis.tsinghua.edu.cn/~huanchen/publications/CMU-CS-20-101.pdf)
3.  [B-Tree vs. Hash Indexing Algorithms: A Comprehensive Analysis](https://myscale.com/blog/b-tree-vs-hash-indexing-algorithms-comprehensive-analysis/)
4.  [A systematic review of deep learning applications in database query ...](https://journalofbigdata.springeropen.com/articles/10.1186/s40537-024-01025-1)
5.  [Modern B-tree techniques - ResearchGate](https://www.researchgate.net/publication/285957257_Modern_B-tree_techniques)
6.  [Search Benchmarking: RediSearch vs. Elasticsearch - Redis](https://redis.io/blog/search-benchmarking-redisearch-vs-elasticsearch/)
7.  [Benchmarking Performance: Elasticsearch vs Competitors - Medium](https://medium.com/gigasearch/benchmarking-performance-elasticsearch-vs-competitors-d4778ef75639)
8.  [Benchmarking Search Performance: Elasticsearch vs competitors](https://blog.gigasearch.co/elasticsearch-against-competitors/)
9.  [Redis vs Elasticsearch - Key Differences - Airbyte](https://airbyte.com/data-engineering-resources/redis-vs-elasticsearch)
10. [Elasticsearch vs. OpenSearch: Vector Search Performance ...](https://www.elastic.co/search-labs/blog/elasticsearch-opensearch-vector-search-performance-comparison)
11. [Navigating Consistency in Distributed Systems: Choosing the Right ...](https://hazelcast.com/blog/navigating-consistency-in-distributed-systems-choosing-the-right-trade-offs/)
12. [Incorporating Latency into CAP Theorem Trade-offs in Distributed ...](https://medium.com/@gurpreet.singh_89/incorporating-latency-into-cap-theorem-trade-offs-in-distributed-system-design-1de74896e29c)
13. [Trading Freshness for Performance in Distributed Systems](https://www.pdl.cmu.edu/PDL-FTP/Database/CMU-CS-14-144.pdf)
14. [Real-Time Indexing RAG | Large-Scale Data - ApX Machine Learning](https://apxml.com/courses/large-scale-distributed-rag/chapter-2-advanced-distributed-retrieval-strategies/near-real-time-indexing-rag)
15. [How does vector space model differs from traditional B-tree indexes](https://cs.stackexchange.com/questions/150568/how-does-vector-space-model-differs-from-traditional-b-tree-indexes)
16. [Inverted Index vs Other Indexes: Key Differences - TiDB](https://www.pingcap.com/article/inverted-index-vs-other-indexes-key-differences/)
17. [Understanding Vector Indexing: A Comprehensive Guide | by MyScale](https://medium.com/@myscale/understanding-vector-indexing-a-comprehensive-guide-d1abe36ccd3c)
18. [Vector Databases: A Beginner's Guide - F22 Labs](https://www.f22labs.com/blogs/vector-databases-a-beginners-guide/)
19. [Evolution of tree data structures for indexing: more exciting than it ...](https://erthalion.info/2020/11/28/evolution-of-btree-index-am/)
20. [optimizing search functionality: a performance comparison between ...](https://www.researchgate.net/publication/387424752_OPTIMIZING_SEARCH_FUNCTIONALITY_A_PERFORMANCE_COMPARISON_BETWEEN_SOLR_AND_ELASTICSEARCH)
21. [Elasticsearch In Action | The Wesleyan Argus](https://www.wesleyanargus.com/fulldisplay/u51CTS/2381982/elasticsearchinaction.pdf)
22. [Elasticsearch vs. Solr: What Developers Need to Know in 2025 - Last9](https://last9.io/blog/elasticsearch-vs-solr/)
23. [Innovative Approaches to Full-Text Search with Solr and Lucene](https://urr.shodhsagar.com/index.php/j/article/download/1336/1389/2702)
24. [Solr vs Elasticsearch: Clash of Open Source Search Engines | Logz.io](https://logz.io/blog/solr-vs-elasticsearch/)
25. [Comparative Analysis of Search Algorithms - ResearchGate](https://www.researchgate.net/publication/333262471_Comparative_Analysis_of_Search_Algorithms)
26. [Electrical Engineering and Computer Science (Course 6) - MIT Bulletin](https://catalog.mit.edu/subjects/6/)
27. [Investigations on Search Methods for Speech Recognition using ...](https://d-nb.info/1054632847/34)
28. [Space Efficient Linear Time Construction of Suffix Arrays.](https://www.researchgate.net/publication/221313870_Space_Efficient_Linear_Time_Construction_of_Suffix_Arrays)
29. [Exploring Storage Engines and Indexing Strategies,LSM-Trees vs. B ...](https://blog.stackademic.com/database-deep-dive-exploring-storage-engines-and-indexing-strategies-lsm-trees-vs-b-trees-268ac1d24056)
30. [B-Tree vs LSM-Tree - TiKV](https://tikv.org/deep-dive/key-value-engine/b-tree-vs-lsm/)
31. [Revisiting B+-tree vs. LSM-tree - USENIX](https://www.usenix.org/publications/loginonline/revisit-b-tree-vs-lsm-tree-upon-arrival-modern-storage-hardware-built)
32. [Write throughput differences in B-tree vs LSM-tree based databases?](https://www.reddit.com/r/databasedevelopment/comments/187cp1g/write_throughput_differences_in_btree_vs_lsmtree/)
33. [What is a LSM Tree? - DEV Community](https://dev.to/creativcoder/what-is-a-lsm-tree-3d75)
34. [A case study of Google Search Engine and Bigtable:Distributed ...](http://norlizakatuk.weebly.com/uploads/2/6/6/0/26606863/apdulrahman.pdf)
35. [Distributed Systems - Jorge Israel Peña](https://jip.dev/notes/distributed-systems/)
36. [Bigtable: A Distributed Storage System for Structured Data](https://research.google.com/archive/bigtable-osdi06.pdf)
37. [SSTable database or big ideas behind the scene | by Danylo Halaiko](https://medium.com/@prajwal_ahluwalia/sstable-database-or-big-ideas-behind-the-scene-1d449a12fb44)
38. [Latency vs. Throughput: Striking the Right Balance in System Design](https://medium.com/@prajwal_ahluwalia/latency-vs-throughput-striking-the-right-balance-in-system-design-a39c66d1ed7d)
39. [Disk-Spill vs. In-Memory Processing: Trade-offs and Considerations](https://www.researchgate.net/publication/390493804_Disk-Spill_vs_In-Memory_Processing_Trade-offs_and_Considerations/download)
40. [Vector databases (4): Analyzing the trade-offs - The Data Quarry](https://thedataquarry.com/blog/vector-db-4)
41. [The Latency/Throughput Tradeoff: Why Fast Services Are Slow And ...](https://blog.danslimmon.com/2019/02/26/the-latency-throughput-tradeoff-why-fast-services-are-slow-and-vice-versa/)
