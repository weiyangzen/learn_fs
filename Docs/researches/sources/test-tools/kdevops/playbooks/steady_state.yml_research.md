# sources/test-tools/kdevops/playbooks/steady_state.yml

Purpose: wrapper playbook for the steady-state storage workflow.

Important APIs/types/functions: targets `all` and invokes role `steady_state`.

Control flow: all inventory hosts run the role.

State/persistence behavior: delegated to steady_state role, including possible destructive device prefill and result collection.

Dependencies/integration: integrates with generated steady-state variables and inventory.

Risks/test signals: broad `hosts: all` means variable gating must prevent accidental device writes. Test signals are role outputs under workflow results.
