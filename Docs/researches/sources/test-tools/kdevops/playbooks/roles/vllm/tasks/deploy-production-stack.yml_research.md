# sources/test-tools/kdevops/playbooks/roles/vllm/tasks/deploy-production-stack.yml

Purpose: deploys vLLM Production Stack through Helm on minikube or an existing Kubernetes cluster, with optional monitoring and autoscaling.

Important APIs/types/functions: includes Kubernetes and Helm setup, `kubernetes.core.helm_repository`, `helm`, `k8s` namespace/HPA resources, template/copy of Helm values, `kubectl cluster-info`, `k8s_info` waits for pods/deployments/services, and monitoring/autoscaling conditionals.

Control flow: sets up Kubernetes and Helm, sets default engine/router images, adds and updates Helm repo, verifies cluster connectivity, optionally switches context, creates local directory and namespace, writes values file, deploys Helm release, waits for engine/router readiness, checks/sets up monitoring components, gathers service endpoints, and optionally creates HPA.

State/persistence behavior: creates namespace, Helm repo cache/release, Kubernetes deployments/services/pods, optional Prometheus/Grafana resources, local values files, and HPA.

Dependencies/integration: depends on vLLM Production Stack chart, Helm, kubectl, `kubernetes.core`, image variables, namespace/release variables, and GPU/CPU inference settings.

Risks/test signals: chart values and image tags may drift; become handling differs for minikube vs existing clusters. Test signals are Helm release success, ready engine/router pods, service list, and monitoring/HPA resources when enabled.
