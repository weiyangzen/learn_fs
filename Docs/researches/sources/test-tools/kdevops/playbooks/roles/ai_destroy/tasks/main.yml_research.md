# sources/test-tools/kdevops/playbooks/roles/ai_destroy/tasks/main.yml

Purpose: Destroys the AI benchmark environment by removing Milvus-related containers, Docker network, storage directories, benchmark results, and optionally images.

Key APIs and flow: Tasks optionally include extra vars, remove Milvus/MinIO/etcd containers with `community.docker.docker_container`, remove the Docker network, delete Docker data directories and benchmark results with `file: state=absent`, remove configured images with `docker_image`, and print completion.

State, dependencies, integration: Destructive host mutations gated mostly by `ai_milvus_docker`. Depends on community.docker collection and variables naming containers, images, network, and paths.

Risks and test signals: Several Docker cleanup steps use `failed_when: false`, so missing Docker or removal failures can be hidden; benchmark results are always removed; path variables must be correct to avoid deleting unintended directories. Tests should cover docker and non-docker modes, undefined variables, idempotent reruns, and check-mode behavior for file deletions.
