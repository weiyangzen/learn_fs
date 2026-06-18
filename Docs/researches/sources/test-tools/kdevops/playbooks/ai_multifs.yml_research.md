# sources/test-tools/kdevops/playbooks/ai_multifs.yml

Purpose: orchestrates multi-filesystem AI benchmark execution on the baseline host.

Important APIs/types/functions: targets `baseline`, gathers facts, escalates privileges, sets `ai_benchmark_results_dir` from `ai_multifs_results_dir` defaulting to `/data/ai-multifs-benchmark`, runs roles `ai_multifs_setup` and `ai_multifs_run`, and prints a final debug summary.

Control flow: facts are collected, storage/test matrices are prepared, benchmarks run across filesystem variants, then a summary is emitted.

State/persistence behavior: creates benchmark outputs under the configured results directory and likely mutates storage formatting/mount state through the roles.

Dependencies/integration: depends on AI multi-filesystem roles, host vars describing filesystem variants, Milvus benchmark tooling, and access to data devices.

Risks/test signals: filesystem setup is high impact and should be validated against disposable devices. Test signals are per-configuration result JSONs, consolidated summaries, and complete iteration counts.
