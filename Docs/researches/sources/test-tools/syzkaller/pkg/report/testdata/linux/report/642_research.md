# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/642

## Purpose
This fixture validates a panicking scheduling-while-atomic report in `exit_to_user_mode_prepare`.

## Important APIs, types, and functions
Important frames include `kernel_fpu_begin_mask` as the preemption-disabled site, `panic`, `__schedule_bug`, `__schedule`, `schedule`, `exit_to_user_mode_prepare`, `syscall_exit_to_user_mode`, and `do_syscall_64`.

## Control flow
A syscall returns toward user mode while preemption remains disabled from FPU handling. The scheduler detects atomic sleep and panic-on-bug behavior reboots the kernel.

## State and persistence behavior
The fixture persists preemption-disabled metadata, no-locks-held state, syscall register data, and `PANICKED: Y`.

## Dependencies and integration points
It tests atomic-sleep parsing for syscall-exit paths and panic marker extraction.

## Risks and test signals
The parser must use `exit_to_user_mode_prepare` rather than `kernel_fpu_begin_mask` as the title frame.
