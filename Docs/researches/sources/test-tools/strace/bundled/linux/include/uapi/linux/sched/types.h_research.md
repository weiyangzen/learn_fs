# sources/test-tools/strace/bundled/linux/include/uapi/linux/sched/types.h

## Purpose

Defines `struct sched_attr`, the extensible ABI used by `sched_setattr(2)` and `sched_getattr(2)` for scheduler policy, deadline scheduling, and utilization clamping.

## Important APIs, Types, and Dependencies

The header includes `linux/types.h`. `SCHED_ATTR_SIZE_VER0` and `SCHED_ATTR_SIZE_VER1` document ABI growth. `struct sched_attr` starts with `size`, then `sched_policy`, `sched_flags`, nice value, realtime priority, deadline runtime/deadline/period fields, and utilization hint fields `sched_util_min` and `sched_util_max`.

## Control Flow, State, and Integration

No executable code is defined. Syscall flow depends on caller-provided `size` for forward/backward compatibility; the kernel reads or writes fields up to the negotiated size. State affected is per-task scheduling policy, realtime/deadline parameters, reset/keep flags, and utilization clamp hints.

## Risks and Test Signals

Risks are failing to initialize `size`, decoding util clamp fields for v0-sized structs, and mixing this extended ABI with legacy `struct sched_param`. Test signals include strace decode of `sched_setattr`/`sched_getattr`, versioned size output, deadline nanosecond fields, and utilization clamp reset values.
