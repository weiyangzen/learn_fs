# sources/test-tools/kdevops/workflows/ai/Makefile

Purpose: Make target layer for the AI workflow. It translates Kconfig symbols into Ansible extra vars and defines setup, benchmark, results, uninstall, destroy, and help targets.

Important variables include `AI_DATA_TARGET`, `AI_ARGS`, `AI_MANUAL_ARGS`, and `AI_ARGS_SEPARATED`. Important targets include `ai`, `ai-baseline`, `ai-dev`, `ai-tests`, `ai-tests-baseline`, `ai-tests-dev`, `ai-tests-results`, `ai-results`, `ai-results-baseline`, `ai-results-dev`, `monitor-results`, `ai-setup`, `ai-uninstall`, `ai-destroy`, and `ai-help-menu`.

Control flow builds `AI_ARGS` from `CONFIG_AI_BENCHMARK_RESULTS_DIR`, `CONFIG_AI_TESTS_VECTOR_DATABASE`, and `CONFIG_AI_VECTOR_DB_MILVUS`. Targets invoke Ansible playbooks with `--extra-vars=@$(KDEVOPS_EXTRA_VARS)` plus inline AI arguments and optional host limits. Benchmark targets run result collection after tests.

State is Make variable expansion, Ansible inventory, extra-vars files, and generated result artifacts. Integration points are playbooks under `playbooks/ai*.yml` and global workflow Make aggregation. Risks include inconsistent host limiting via `HOSTS` versus `LIMIT_HOSTS`, hardcoding Milvus Docker true when Milvus enabled, and shell quoting of inline extra vars. Test signals should use `make -n` for baseline/dev/all targets and assert expected playbooks and vars.
