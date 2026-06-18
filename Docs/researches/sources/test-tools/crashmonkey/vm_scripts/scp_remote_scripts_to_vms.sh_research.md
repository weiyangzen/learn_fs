# sources/test-tools/crashmonkey/vm_scripts/scp_remote_scripts_to_vms.sh

Purpose: copies all `vm_remote_*` scripts and `cm_cleanup.sh` to each local NAT-forwarded VM.

Important APIs/types/functions: environment `num_vms`, `sshpass -p "password" scp`, `StrictHostKeyChecking no`, files `~/vm_remote_*` and `~/cm_cleanup.sh`, user `user`, ports from 3022.

Control flow: prints target VM count, loops VMs, copies remote scripts and cleanup script, then increments port. State/persistence behavior: updates scripts in VM home directories.

Dependencies/integration: run during setup and before workload distribution. Risks/test signals: hard-coded password, broad globs, no failure checks, and assumes scripts live in the caller's home directory.
