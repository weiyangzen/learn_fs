# sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range_parallel.sh

Purpose: removes the shared segmented workload directory and starts background range partitioners for batches of servers.

Important APIs/types/functions: args `num_per_vm`, `max_workload`, workload base path, `batch_size`, `num_servers`, `rm -r workloads/seg`, and `nohup ./segregate_workloads_range.sh ...`.

Control flow: deletes `workloads/seg`, computes server ranges, launches one background range script per batch, and increments the range. State/persistence behavior: destructively resets and recreates local workload partitions via children.

Dependencies/integration: used before parallel SCP distribution. Risks/test signals: multiple background scripts write under the same tree without coordination, no wait/failure handling, and `rm -r` can fail or remove unintended content if run from the wrong directory.
