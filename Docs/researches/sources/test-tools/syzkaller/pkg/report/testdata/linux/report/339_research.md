<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/339 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/339

## Purpose
This fixture covers a general protection fault caused by sysrq crash handling. The expected title is `general protection fault in sysrq_handle_crash`, alt `bad-access in sysrq_handle_crash`, type `DoS`, and panicked.

## Important APIs, Types, And Functions
The stack is anchored at `RIP: sysrq_handle_crash+0x5e/0xd0`, then `__handle_sysrq`, `write_sysrq_trigger`, `proc_reg_write`, `__vfs_write`, `vfs_write`, `ksys_write`, and syscall return. It later includes `Kernel panic - not syncing: Fatal exception`.

## Control Flow
The reporter must select the initial GPF report before the fatal-exception panic, normalize the bad-access alt, and mark the crash panicked due to the later panic line.

## State And Persistence
The expected metadata is persisted in the header. Runtime state is a sysrq-trigger write that causes the kernel exception and panic.

## Dependencies And Integration Points
It depends on x86 exception parsing, bad-access alt generation, sysrq symbol handling, and panic-after-oops detection.

## Risks
If panic lines take precedence over the GPF, the title would become generic and lose the faulting function.

## Test Signals
The parser should return the GPF title in `sysrq_handle_crash` and keep `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/339 -->
