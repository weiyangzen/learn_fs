# sources/test-tools/crashmonkey/vm_scripts/restart_read_only_vms.sh

Purpose: probes local NAT-forwarded VMs for read-only filesystem symptoms and restarts affected VMs.

Important APIs/types/functions: environment `num_vms`, ports from 3022, `timeout rsh`, remote `touch /home/user/a`, grep `Read-only`, `force_stop_vm.sh`, `start_particular_vm.sh`, and sleeps.

Control flow: loops VMs, executes a remote touch command, treats empty output or output containing `Read-only` as bad, kills/restarts the VM and waits; otherwise prints fine. State/persistence behavior: creates `/home/user/a` on healthy VMs and restarts unhealthy ones.

Dependencies/integration: maintenance script for long distributed runs. Risks/test signals: `num_vms=$num_vms` relies on exported environment, unquoted tests can misbehave, and restart is forceful.
