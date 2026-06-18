# File Research: sources/os/bsd/openbsd-src/sys/sys/futex.h

This header defines the OpenBSD futex syscall ABI.

Key definitions:
- Userland prototype: `futex(volatile uint32_t *, int, int, const struct timespec *, volatile uint32_t *)`.
- Operation masks/constants: `FUTEX_OP_MASK`, `FUTEX_WAIT`, `FUTEX_WAKE`, `FUTEX_REQUEUE`.
- Flag mask and private flag: `FUTEX_FLAG_MASK`, `FUTEX_PRIVATE_FLAG`.
- Convenience private operations: `FUTEX_WAIT_PRIVATE`, `FUTEX_WAKE_PRIVATE`, `FUTEX_REQUEUE_PRIVATE`.

Risk notes:
- The syscall accepts volatile user addresses; kernel implementation must validate and safely fault/copy user memory.
- Private futex operations alter sharing/lookup semantics and must not be confused with process-shared futexes.
