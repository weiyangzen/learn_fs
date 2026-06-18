# sources/test-tools/crashmonkey/vm_scripts/extract_core_workload.sh

Purpose: filters generated workload C++ source down to core filesystem operations for easier inspection.

Important APIs/types/functions: one argument `file`, `cat`, `grep -v user_tools`, and grep patterns for link/unlink/mkdir/sync/Rename/WriteData/Open/checkpoint/FALLOC.

Control flow: validates one argument, then streams matching lines from the file. State/persistence behavior: read-only; prints to stdout.

Dependencies/integration: useful for reviewing generated ACE workloads. Risks/test signals: pattern matching is approximate, case-sensitive except separate `sync`/`Sync`, and it can miss operations not in the hard-coded grep list.
