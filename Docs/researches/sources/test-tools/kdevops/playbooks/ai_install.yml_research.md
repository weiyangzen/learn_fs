# sources/test-tools/kdevops/playbooks/ai_install.yml

Purpose: installs Milvus vector database infrastructure for AI benchmarks.

Important APIs/types/functions: targets `baseline:dev` with privilege escalation and runs roles `ai_docker_storage`, `ai_milvus_storage`, and `milvus`. Storage roles are gated by `ai_docker_storage_enable | default(true)` and `ai_milvus_storage_enable | default(false)`.

Control flow: prepare Docker storage, optionally prepare Milvus-specific storage, then install/configure Milvus through the shared role.

State/persistence behavior: can format/mount or configure Docker data storage and create persistent Milvus containers, volumes, and configuration.

Dependencies/integration: integrates host var filesystem matrices, Docker, Milvus role defaults, and AI benchmark playbooks.

Risks/test signals: storage preparation can be invasive if device/path variables are wrong. Test signals are successful role completion, running Milvus service, and reachable port 19530 for later benchmarks.
