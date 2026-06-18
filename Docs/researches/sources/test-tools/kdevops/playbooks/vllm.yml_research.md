# sources/test-tools/kdevops/playbooks/vllm.yml

Purpose: wrapper playbook for deploying and managing vLLM Production Stack or related deployment modes.

Important APIs/types/functions: targets `baseline:dev`, escalates with sudo, sets `ansible_ssh_pipelining`, conditionally runs `create_data_partition`, then role `vllm`.

Control flow: creates data partition when a data device is configured, then delegates deployment/benchmark/cleanup to vLLM role.

State/persistence behavior: delegated to data partition and vLLM roles, including Docker/Kubernetes/systemd/data/result state.

Dependencies/integration: depends on inventory groups, `data_device`, and vLLM generated variables.

Risks/test signals: data partition role may format storage before vLLM tasks. Test signals are successful role deployment and benchmark artifacts.
