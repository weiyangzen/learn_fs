# sources/test-tools/syzkaller/syz-agent/k8s/overlays/minikube/agent-config.json

Purpose: local/minikube syz-agent configuration.

Important APIs/types/functions: JSON config with dashboard, env-resolved secrets, cache size, and one `linux/amd64` qemu target.

Control flow: loaded by syz-agent via ConfigMap. Uses buildroot amd64 disk image, upstream apparmor KASAN kernel config, qemu with KVM and 2 CPUs/2GiB RAM.

State and persistence: cache size limited to 32GB; runtime state resides in agent workdir PVC.

Dependencies and integration points: requires `GOOGLE_API_KEY` and `DASHBOARD_KEY` env injection from minikube kustomization.

Risks: connects to production syzbot URL even in minikube. Small VM memory may affect workflow coverage.

Test signals: agent config load and dashboard job polling in local deployment.
