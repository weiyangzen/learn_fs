# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/setup-kubernetes.yml

Purpose: installs kubectl/minikube/crictl as needed and prepares either minikube or an existing Kubernetes cluster for vLLM.

Important APIs/types/functions: `stat`, shell/curl version discovery, downloads/install commands, veth kernel config/module checks, Docker socket permission, user/group tasks, file/sysctl setup, `minikube start/status/addons`, `kubectl cluster-info`, and GPU resource checks.

Control flow: installs kubectl if missing; for minikube, installs minikube and crictl, validates Docker/veth support, cleans stopped minikube containers, fixes permissions and sysctl, ensures kdevops Docker group and `/data/minikube`, starts minikube with configured resources, waits ready, and enables addons. For existing clusters, verifies connectivity and optionally checks GPU resources.

State/persistence behavior: writes binaries under `/usr/local/bin`, changes Docker socket permissions/group membership, writes `/data/minikube`, sets sysctl, creates or modifies minikube cluster, and changes Kubernetes context/state.

Dependencies/integration: included by Docker and production-stack vLLM deployments. Depends on Docker, kernel veth support, minikube/kubectl networks, and kdevops user assumptions.

Risks/test signals: broad Docker socket permissions, kernel-module assumptions, and remote latest-version downloads are risks. Test signals are `kubectl cluster-info`, minikube ready state, enabled addons, and detected GPU resources when required.
