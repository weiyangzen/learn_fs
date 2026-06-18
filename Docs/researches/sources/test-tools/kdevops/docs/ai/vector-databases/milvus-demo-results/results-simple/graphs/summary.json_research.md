# sources/test-tools/kdevops/docs/ai/vector-databases/milvus-demo-results/results-simple/graphs/summary.json

Purpose: compact graph summary for a simple Milvus AI benchmark result set. It records what configurations were graphable and the headline insert/query throughput values used by generated visual reports.

Important APIs/types/functions: top-level keys are `total_tests`, `filesystems_tested`, `configurations`, and `performance_summary`. `configurations` maps names such as `btrfs-default-baseline` and `btrfs-default-dev` to `insert_qps`, `query_qps`, and `host`. `performance_summary` stores best insert/query QPS and averages.

Control flow: graph generation reads individual benchmark outputs, reduces them into per-configuration metrics, writes this summary beside generated graph images, and downstream documentation can render it without reprocessing raw Milvus results.

State/persistence behavior: persisted state is an aggregate snapshot: 80 tests, filesystem list `btrfs`, best insert QPS 64,494.85, best query QPS 1,093.65, average insert QPS 52,354.44, and average query QPS 850.62. Host is `unknown`, so host attribution is not reliable.

Dependencies/integration: belongs to the simple results graph directory and complements the AI result collection and graphing pipeline. Consumers should treat it as derived data and prefer raw result files when auditing regressions.

Risks/test signals: incomplete host metadata and a single filesystem list limit comparisons. Test signals are valid JSON, non-empty `configurations`, nonzero QPS fields, and consistency between best values and the underlying graph data.
