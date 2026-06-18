# sources/test-tools/kdevops/workflows/vllm/Makefile

Purpose: Makefile entry points for the kdevops vLLM workflow. It wraps `playbooks/vllm.yml` with focused tag sets for deploy, benchmark, monitor, teardown, cleanup, results collection, status inspection, quick testing, and help output.

Important APIs/types/functions: GNU make targets, `HELP_TARGETS += vllm-help-menu`, `$(Q)` quiet prefix, recursive `$(MAKE)`, `ansible-playbook`, `ansible`, `kubectl`, `helm`, `docker`, `grep`, `ps`, and helper scripts `scripts/vllm-status-summary.py` and `scripts/vllm-quick-test.sh`.

Control flow: `vllm` and `vllm-deploy` run the same Ansible playbook with data partition, vars, dependency, Docker config, and deploy tags. Benchmark, monitor, teardown, cleanup, and result targets use narrower tag lists. Cleanup variants pass extra JSON variables to remove binaries or purge data. `vllm-status` emits diagnostic sections and runs remote shell checks against all hosts. `vllm-status-simplified` pipes detailed status through a Python summarizer. `vllm-help-menu` prints the workflow command list.

State/persistence behavior: most targets mutate remote or guest state through Ansible. They depend on `extra_vars.yaml`, inventory `hosts`, and deployment artifacts such as `/data/vllm/prod-stack-values.yaml`, Kubernetes namespaces, Helm releases, Docker images, and benchmark result directories. The Makefile itself stores no durable state.

Dependencies/integration: integrates the vLLM Kconfig/YAML output with `playbooks/vllm.yml`. It assumes baseline/dev inventory groups, Ansible access to nodes, Kubernetes and Helm commands on target nodes, optional Minikube, Docker, and the support scripts named above.

Risks/test signals: status commands suppress many errors with `2>/dev/null || echo`, making them useful for humans but weak for CI gating. Namespace checks are hard-coded to `vllm-system`, which can diverge from `VLLM_HELM_NAMESPACE`. Test signals include `make vllm-help-menu`, dry or targeted Ansible tag runs, `make vllm-status-simplified`, quick API test success, and cleanup idempotence.
