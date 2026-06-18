# sources/test-tools/strace/src/affinity.c

Purpose: decodes CPU affinity masks for `sched_setaffinity` and `sched_getaffinity`.

Important APIs/types/functions: `get_cpuset_size`, `print_affinitylist`, `SYS_FUNC(sched_setaffinity)`, `SYS_FUNC(sched_getaffinity)`, `sched_getaffinity`, `next_set_bit`, `umoven_or_printaddr`, `tprint_bitset_*`, and `printpid`.

Control flow: `get_cpuset_size` lazily probes a kernel-accepted affinity mask size by calling `sched_getaffinity` with NULL until errors shift from `EINVAL`. `print_affinitylist` validates verbosity/error/address/length, copies the mask, prints set CPU indexes, and adds an ellipsis marker when user length exceeds copied size. `sched_getaffinity` prints pid/size on entry and the returned mask on exit using `tcp->u_rval` as length.

State and persistence behavior: static cached `cpuset_size` persists within the strace process. Per-call allocations are freed after printing.

Dependencies and integration points: uses Linux scheduler API behavior, generic bitset helpers, syscall enter/exit state, and current personality word size.

Risks: the probing relies on undocumented kernel behavior. Very large `len` values are bounded by probed max for copying but still affect ellipsis output. Allocation failure falls back to raw address.

Test signals: affinity syscall tests should verify empty sets, populated masks, oversized masks with more-data marker, failed `sched_getaffinity`, and nonverbose/raw address paths.
