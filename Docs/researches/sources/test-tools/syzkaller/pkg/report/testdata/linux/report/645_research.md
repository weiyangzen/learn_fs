# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/645

## Purpose
This fixture is another panicking `exit_to_user_mode_prepare` scheduling-while-atomic sample.

## Important APIs, types, and functions
Key frames are `kernel_fpu_begin_mask`, `panic`, `__schedule_bug`, `__schedule`, `schedule`, `exit_to_user_mode_prepare`, `syscall_exit_to_user_mode`, `do_syscall_64`, and syscall return assembly.

## Control flow
The report follows syscall exit while atomic scheduling is detected, with the preemption-disabled site pointing to kernel FPU state setup.

## State and persistence behavior
The file persists panic classification, preemption-disabled metadata, and syscall register state.

## Dependencies and integration points
It provides duplicate coverage for syscall-exit atomic-sleep parser behavior and panic-on-scheduling-bug recognition.

## Risks and test signals
The expected title must remain `BUG: scheduling while atomic in exit_to_user_mode_prepare` with `PANICKED: Y`.
