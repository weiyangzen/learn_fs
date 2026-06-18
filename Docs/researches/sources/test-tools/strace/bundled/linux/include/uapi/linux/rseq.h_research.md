# sources/test-tools/strace/bundled/linux/include/uapi/linux/rseq.h

## Purpose

Defines the restartable sequences userspace ABI. strace uses it to decode `rseq(2)` registration arguments and to understand the task-local shared memory layout the kernel updates on CPU migration or critical-section aborts.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `asm/byteorder.h`. It exports `enum rseq_cpu_id_state`, `enum rseq_flags`, `enum rseq_cs_flags_bit`, and `enum rseq_cs_flags` for migration/no-restart-on-signal/preempt/migrate behavior. `struct rseq_cs` describes one critical section with version, flags, start IP, post-commit offset, and abort IP. `struct rseq_slice_ctrl` describes the slice extension state. `struct rseq` contains cpu id start/current fields, current `rseq_cs` pointer, flags, node id, mm cids, and embedded slice control.

## Control Flow, State, and Integration

Runtime flow is userspace registering a per-thread `struct rseq`, then placing critical-section descriptors where the kernel can abort or update CPU identity around preemption, signal, and migration events. State is per-thread and memory-mapped/shared with the kernel, not persisted to disk.

## Risks and Test Signals

Risks include ABI alignment mistakes, endian-specific field interpretation, stale cpu id use, failing to reset `rseq_cs` after abort, and decoding the slice extension as always present without considering size negotiated by syscall arguments. Test signals include `rseq` syscall decode with flags, structure-size handling, and named critical-section flags.
