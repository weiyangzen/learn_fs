# sources/test-tools/crashmonkey/vm_scripts/segregate_workloads.sh

Purpose: partitions generated `j-lang<N>.cpp` workloads across servers and VMs into a directory tree suitable for later SCP distribution.

Important APIs/types/functions: args `num_per_vm`, start workload `k`, max workload, workload base path, output path, `live_nodes`, fixed `num_vms=12`, `mkdir -p`, `cp`.

Control flow: removes the output path, loops nodes from `live_nodes`, creates `node<i>-<ip>/vm<j>` directories, copies `num_per_vm` sequential workloads into each VM directory, and stops once `k > max`.

State/persistence behavior: deletes and recreates local workload partition directories. Dependencies/integration: feeds `scp_segregated_workloads.sh`.

Risks/test signals: destructive `rm -r` without existence/guard, no missing-file checks, fixed 12 VMs per node, and no quoting of paths.
