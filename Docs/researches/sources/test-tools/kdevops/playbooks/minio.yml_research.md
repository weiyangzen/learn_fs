# sources/test-tools/kdevops/playbooks/minio.yml

Purpose: complete MinIO S3 storage benchmarking playbook covering install, benchmark, uninstall, destroy, and result analysis phases.

Important APIs/types/functions: five plays target `baseline:dev` with root privilege. Roles are `minio_install`, `minio_setup`, `minio_warp_run`, `minio_uninstall`, `minio_destroy`, and `minio_results`. Setup passes container image/name, API/console ports, credentials, data path, memory limit, and Docker network. Benchmark play optionally imports monitoring run/collect tasks.

Control flow: install and configure MinIO, run Warp benchmarks with optional monitoring around them, provide uninstall/destroy phases, and analyze results.

State/persistence behavior: creates Docker/container state, MinIO data path contents, benchmark results, and optional monitoring data. Destroy roles can remove persistent storage depending on role policy.

Dependencies/integration: tied to MinIO Kconfig, Docker, Warp benchmark tooling, baseline/dev inventory, and monitoring configuration.

Risks/test signals: credentials and data paths are passed directly as variables; destructive phases share the same file and must be tag-controlled. Test signals are running MinIO service, Warp result files, monitoring artifacts when enabled, and clean teardown when uninstall/destroy tags are used.
