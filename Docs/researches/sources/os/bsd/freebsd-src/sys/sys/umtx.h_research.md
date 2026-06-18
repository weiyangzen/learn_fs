# File Research: sources/os/bsd/freebsd-src/sys/sys/umtx.h

Userland synchronization object syscall ABI header.

Key responsibilities:
- Defines common umtx, umutex, rwlock, and semaphore state bits and flags, including contested, priority inheritance/protect, robust, non-consistent, process-shared, reader preference, waiter bits, and count masks.
- Documents mutex owner word layout: high bit as contention indicator and remaining bits as owner TID, with low values reserved for special markers.
- Defines `_umtx_op` operation codes for waits, wakes, mutexes, condition variables, rwlocks, private variants, semaphores, shared memory, robust lists, and minimum timeout operations.
- Defines operation modifier flags for i386/32-bit handling and flags for condition-variable waits, absolute timeout, unpark checking, and umtx shared-memory operations.
- Defines robust-list parameter structure.
- Declares `_umtx_op()` and `_umtx_op_err()`.

Dependencies:
- Includes `sys/_umtx.h`.

Notable risks:
- Numeric operation codes and bit layouts are user/kernel ABI and also consumed by tracing/decoding tools.
- Robust mutex owner-dead/not-recoverable encodings share contested-bit space and require precise userspace/kernel interpretation.
