# sources/test-tools/kdevops/workflows/ai/Kconfig

Purpose: Kconfig configuration for the AI workflow, currently centered on Milvus vector database performance testing.

Important symbols include `AI_TESTS_VECTOR_DATABASE`, `AI_VECTOR_DB_MILVUS`, `AI_VECTOR_DB_MILVUS_QUICK_TEST`, Docker-only Milvus settings, version/port/collection/dimension/dataset/batch/query counts, `AI_BENCHMARK_RESULTS_DIR`, graphing enablement, `AI_BENCHMARK_ITERATIONS`, Docker storage inclusion, and optional `AI_MULTIFS_ENABLE`.

Control flow is nested Kconfig choices and conditionals under `KDEVOPS_WORKFLOW_ENABLE_AI`. Selecting vector database tests also selects baseline/dev comparison. Quick-test mode can be forced by CLI detection through `scripts/check-cli-set-var.sh`; it reduces dataset size and iteration count for CI/demo runs. Docker, docker-storage, native, and multifs fragments are sourced based on symbols.

State persists as yaml output consumed by Ansible and Make. Risks include `AI_VECTOR_DB_MILVUS_NATIVE` being referenced without definition in this file, typo in help text, storage consumption defaults near 100 GiB, and Docker-only assumptions. Test signals should parse Kconfig, test quick-mode defaults, and verify generated yaml drives `workflows/ai/Makefile` correctly.
