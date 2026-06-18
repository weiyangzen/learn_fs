# File Research: sources/os/bsd/netbsd-src/sys/sys/futex.h

Read completely: 184 lines.

## Purpose
Defines NetBSD's Linux-compatible futex ABI plus robust futex metadata and kernel routines.

## Main Interfaces
- Commands: `FUTEX_WAIT`, `WAKE`, `FD`, `REQUEUE`, `CMP_REQUEUE`, `WAKE_OP`, PI and bitset variants.
- Flags: `FUTEX_PRIVATE_FLAG`, `FUTEX_CLOCK_REALTIME`, `FUTEX_CMD_MASK`.
- Wake-op encoding: `FUTEX_OP`, masks, operations, comparison operators.
- Robust futex word bits: `FUTEX_WAITERS`, `FUTEX_OWNER_DIED`, `FUTEX_SYNCOBJ_*`, `FUTEX_TID_MASK`, `FUTEX_BITSET_MATCH_ANY`.
- Robust-list ABI offsets and sizes.
- Optional libc-private robust-list structs.
- Kernel routines: `futex_robust_head_lookup`, `futex_release_all_lwp`, `do_futex`, `futex_sys_init`, `futex_sys_fini`.

## Dependencies And Integration
Includes `sys/timespec.h`. Integrates with LWP lifecycle and Linux-compat synchronization behavior.

## Risks And Edge Cases
- Robust futex ABI is specified as three longwords and has separate 32-bit size.
- `FUTEX_SYNCOBJ_*` reserves high TID bits, reducing max encoded thread id.
- PI futex entries are distinguished by the low bit of list entries.

## Filesystem Relevance
Low direct relevance. It is process synchronization infrastructure, not filesystem code.
