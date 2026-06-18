# sources/test-tools/crashmonkey/vm_scripts/segregate_workloads_range.sh

Purpose: partitions workloads for only a selected range of server indices while preserving global workload numbering offsets for skipped servers.

Important APIs/types/functions: args `num_per_vm`, `max`, workload base path, start server, end server, fixed `num_vms=12`, `live_nodes`, and output `workloads/seg/node<i>-<ip>/vm<j>`.

Control flow: loops all live nodes with global server index and workload counter. For skipped servers it advances `k` by `num_vms * num_per_vm`; for included servers it creates directories and copies sequential `j-lang<k>.cpp` files until max.

State/persistence behavior: creates/updates `workloads/seg` subdirectories but does not remove the root. Dependencies/integration: used by the parallel range wrapper.

Risks/test signals: arithmetic uses escaped `expr` multiplication, missing source files are not handled, fixed VM count, and output from parallel invocations can interleave.
