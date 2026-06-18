# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-docker.yml

Purpose: deploys a basic vLLM Kubernetes manifest using Docker/minikube or an existing Kubernetes environment.

Important APIs/types/functions: Docker service/group/permission tasks, `include_tasks: setup-kubernetes.yml`, `file`, image mirror `set_fact`, manifest `template`, `kubectl apply`, `kubernetes.core.k8s_info`, and service endpoint reporting.

Control flow: ensures Docker is running and current user can access it, sets up Kubernetes when requested, creates local/results directories, resolves image path with optional mirror, renders deployment manifest, applies it with kubectl, waits for pods by label, reads `vllm-service`, and displays endpoint information.

State/persistence behavior: mutates Docker group/socket permissions, creates Kubernetes resources, writes manifest under local vLLM path, and creates result directories.

Dependencies/integration: depends on Docker, kubectl, Kubernetes/minikube setup, templates, `kubernetes.core`, and image variables.

Risks/test signals: chmodding Docker socket is broad; Kubernetes namespace/context assumptions can misdeploy. Test signals are `kubectl apply` changed/created output, ready pods, and service info.
