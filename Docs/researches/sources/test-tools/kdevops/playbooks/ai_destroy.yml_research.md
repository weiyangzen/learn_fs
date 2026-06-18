# sources/test-tools/kdevops/playbooks/ai_destroy.yml

Purpose: destroys Milvus vector database runtime artifacts on baseline and dev systems.

Important APIs/types/functions: targets `baseline:dev` with `become: true`, uses `community.docker.docker_compose` to stop containers when `ai_vector_db_milvus_docker` is true, and `ansible.builtin.file` over a loop to remove data directories when `ai_vector_db_force_destroy` is true.

Control flow: stop the Docker Compose stack first, then optionally remove persistent Milvus data paths only under an explicit force flag.

State/persistence behavior: mutates Docker container state and can delete benchmark database storage. Without `ai_vector_db_force_destroy`, data directories should remain.

Dependencies/integration: depends on Docker Compose support, Milvus role variables that define compose project/data paths, and baseline/dev inventory.

Risks/test signals: force deletion is destructive and variable mistakes could remove the wrong path. Test signals are stopped containers, absent targeted directories only under force, and idempotent no-op behavior on repeat runs.
