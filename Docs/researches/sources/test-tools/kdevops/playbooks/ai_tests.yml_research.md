# sources/test-tools/kdevops/playbooks/ai_tests.yml

Purpose: end-to-end AI test entrypoint covering Milvus setup, benchmark execution, and result collection.

Important APIs/types/functions: three plays target `baseline:dev` with `become: true`. They run role `milvus` when `ai_vector_db_milvus` is true, role `ai_run_benchmarks` with `ai_skip_setup: true`, and role `ai_collect_results` when `ai_collect_results | default(true)` is true.

Control flow: ensure Milvus exists, run benchmarks without repeating setup, then collect results.

State/persistence behavior: can change service/container state through Milvus setup, generate benchmark result files, and write collected summaries.

Dependencies/integration: connects Make `ai-tests` targets to Milvus and AI result roles and shares inventory variables with `ai_install.yml`.

Risks/test signals: the variable name `ai_collect_results` is both a role name and a boolean condition, which can confuse readers and variable management. Test signals are three-play execution, generated benchmark outputs, and final collected artifacts.
