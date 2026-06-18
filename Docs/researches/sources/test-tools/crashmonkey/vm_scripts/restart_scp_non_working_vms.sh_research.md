# sources/test-tools/crashmonkey/vm_scripts/restart_scp_non_working_vms.sh

Purpose: checks whether SCP to each local NAT-forwarded VM works and restarts VMs where SCP fails.

Important APIs/types/functions: environment `num_vms`, `sshpass scp`, timeout 10, files `~/vm_remote_*`, `force_stop_vm.sh`, `start_particular_vm.sh`, and NAT ports from 3022.

Control flow: loops over VM ports, attempts to copy remote scripts to each VM, checks exit status, restarts failing VMs, waits, and increments the port. State/persistence behavior: copies scripts to VM home directories and force-restarts failing VMs.

Dependencies/integration: used before distributing workloads. Risks/test signals: hard-coded password/user, broad source glob, no cleanup of copied files, and failure may be due to network/load rather than VM health.
