# File Research: sources/os/bsd/dragonflybsd/sys/sys/posix4.h

Kernel-only POSIX.1b/POSIX.4 scheduling support declarations.

Key responsibilities:
- Rejects userland inclusion.
- Includes `opt_posix.h` and `sys/sched.h`.
- Declares `M_P31B` malloc type and `p31b_setcfg()`.
- Under `_KPOSIX_PRIORITY_SCHEDULING`, defines scheduler operation enum and read/write access vector.
- Declares `struct ksched` lifecycle and operation functions for POSIX scheduling parameter, scheduler policy, yield, priority min/max, and round-robin interval operations.

Important behavior:
- `KSCHED_OP_RW` encodes which operations need write access.
- Scheduler APIs operate on `struct lwp` and return through `register_t *` where needed.

Dependencies:
- Kernel config option `_KPOSIX_PRIORITY_SCHEDULING`.
- Uses `struct proc`, `struct lwp`, `struct sched_param`, `timespec`, and `register_t`.

Notable risks:
- Behavior is compile-option dependent.
- Access-mode vector must remain synchronized with `enum ksched_op` order.
