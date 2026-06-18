# sources/test-tools/kdevops/playbooks/rxe.yml

Purpose: wrapper playbook for configuring software-emulated RoCE RDMA over Ethernet.

Important APIs/types/functions: targets `baseline:dev` and invokes role `rxe`.

Control flow: Ansible selects baseline/dev hosts and transfers execution to the role.

State/persistence behavior: delegated to role `rxe`, likely udev/module/network configuration.

Dependencies/integration: integrates with kdevops inventory host groups and RDMA role.

Risks/test signals: wrapper risk is host group or role-name drift. Test signals are Ansible role discovery and resulting rxe device/module state.
