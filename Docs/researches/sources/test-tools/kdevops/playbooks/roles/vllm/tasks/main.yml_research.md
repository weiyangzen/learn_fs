# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/main.yml

Purpose: top-level vLLM workflow dispatcher for setup, deployment, benchmarking, monitoring, cleanup, results collection, and visualization.

Important APIs/types/functions: roles `create_data_partition` and `docker_mirror_9p`, `set_fact`, includes for install deps, Docker data config, Docker/production-stack/bare-metal deployments, benchmark script template, async port forwarding, benchmark command, `k8s`/`helm` cleanup, `fetch`, and visualization template/command.

Control flow: prepares data/mirror roles, sets workflow variables, installs dependencies, configures Docker data root for Docker-like deployments, branches to selected deployment type, optionally runs benchmarks with port-forwarding when needed, reports monitoring endpoints, performs cleanup/teardown when requested, collects result and system-info files, and optionally generates HTML visualization.

State/persistence behavior: delegates deployment state to Docker/Kubernetes/systemd tasks, creates benchmark scripts/results under vLLM paths, may delete Kubernetes resources or bare-metal services, and fetches results to the controller.

Dependencies/integration: depends on vLLM defaults, deployment type variables, templates, Kubernetes/Helm/Docker/systemd tasks, and generated kdevops workflow flags.

Risks/test signals: many flags share one task file, so conflicting deploy/cleanup/result modes can produce surprising behavior. Test signals are selected include output, benchmark JSON/results, service endpoints, fetched artifacts, and visualization HTML.
