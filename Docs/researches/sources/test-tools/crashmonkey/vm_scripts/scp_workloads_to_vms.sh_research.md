# sources/test-tools/crashmonkey/vm_scripts/scp_workloads_to_vms.sh

Purpose: distributes local `~/seq2/vm<N>` workload sets to each local NAT-forwarded VM after first copying remote helper scripts.

Important APIs/types/functions: environment `num_vms`, `scp_remote_scripts_to_vms.sh`, `rsh` cleanup/create commands, `scp -P`, user `user`, ports from 3022.

Control flow: copies remote scripts to all VMs, loops VMs, removes and recreates `~/seq2` remotely, copies workload files for that VM, increments port, and prints completion. State/persistence behavior: replaces per-VM remote workload directories.

Dependencies/integration: expects local workload partitioning under `~/seq2/vm<i>`. Risks/test signals: no error handling, destructive `rm -r ~/seq2`, hard-coded user/ports, and no quoting around globs.
