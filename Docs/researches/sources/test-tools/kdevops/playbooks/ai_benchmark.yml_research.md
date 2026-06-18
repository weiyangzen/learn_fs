# sources/test-tools/kdevops/playbooks/ai_benchmark.yml

Purpose: runs Milvus vector database benchmarks on baseline and dev hosts.

Important APIs/types/functions: play targets `baseline:dev`, sets `ai_vector_db_milvus_benchmark_enable: true`, invokes role `milvus` with tags `ai`, `vector_db`, `milvus`, and `benchmark`, and conditionally imports `roles/monitoring/tasks/monitor_collect.yml` when `enable_monitoring` is true.

Control flow: Ansible applies the Milvus role in benchmark mode, then optionally collects monitoring data. It does not install storage roles, so it expects Milvus setup to be complete.

State/persistence behavior: benchmark output is persisted by the Milvus role, typically under workflow result directories, and monitoring collection may persist `/root/monitoring` data or fetched local copies.

Dependencies/integration: depends on the `milvus` role, AI variables, inventory groups `baseline` and `dev`, and optional monitoring role tasks.

Risks/test signals: running without prior install/setup can fail or benchmark a stale service. Test signals are generated benchmark JSONs, nonzero QPS metrics, and optional monitoring artifacts after collection.
