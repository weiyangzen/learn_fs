# sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads_parallel.sh

Purpose: starts multiple background SCP jobs to distribute segregated workloads across server batches.

Important APIs/types/functions: args `batch_size`, `num_servers`, `seg_path`, range variables, and `nohup ./scp_segregated_workloads.sh ... > out<i>.log &`.

Control flow: partitions server indices into ranges and launches the nonparallel copy script for each range in the background. State/persistence behavior: creates logs and remote workload copies via child scripts.

Dependencies/integration: wrapper around `scp_segregated_workloads.sh`. Risks/test signals: no synchronization or failure aggregation, and parallel jobs may overload network or remote SSH.
