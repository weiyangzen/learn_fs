<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/270 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/270

## Purpose
This fixture verifies RCU stall parsing for the input subsystem mouse device write path. The expected title is `INFO: rcu detected stall in mousedev_write`, alt `stall in mousedev_write`, and type `HANG`.

## Important APIs, Types, and Functions
The log contains an `rcu_sched self-detected stall on CPU` with NMI backtrace. Parser paths include RCU stall detection, IRQ stack skipping, and hang-title generation. Key symbols include `dump_stack`, `nmi_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall`, `rcu_check_callbacks`, `_raw_spin_unlock_irq`, `mousedev_write`, `__vfs_write`, `vfs_write`, `ksys_write`, `__x64_sys_write`, and `do_syscall_64`.

## Control Flow
The reporter reads the RCU stall header, passes through timer/IRQ frames, and extracts `mousedev_write` from the task stack as the hang site.

## State and Persistence Behavior
The fixture is immutable and stores expected title, alt, and HANG type. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux RCU stall regexes and function-priority rules for write syscall stacks.

## Risks and Edge Cases
The top RIP is `_raw_spin_unlock_irq`, which is too generic. The parser must prefer `mousedev_write` instead of write syscall wrappers.

## Test Signals
Output should be `INFO: rcu detected stall in mousedev_write`, alt `stall in mousedev_write`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/270 -->
