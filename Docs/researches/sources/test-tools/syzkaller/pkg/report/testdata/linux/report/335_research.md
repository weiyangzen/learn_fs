<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/335 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/335

## Purpose
This fixture verifies lockdep warning parsing when the log is known corrupted by fault injection and panic-on-warn. The expected title is `WARNING: locking bug in corrupted`, type `LOCKDEP`, with corrupted and panicked flags.

## Important APIs, Types, And Functions
The log begins with `FAULT_INJECTION: forcing a failure`, then a warning at `kernel/locking/lockdep.c:3553 lock_downgrade`. The surrounding syscall path includes tty and ioctl frames such as `__tty_buffer_request_room`, `n_tty_ioctl`, `tty_ioctl`, `ksys_ioctl`, and a user RIP.

## Control Flow
The reporter must notice the warning and lockdep context, but because corruption prevents reliable function attribution, it uses `corrupted` in the title. The panic-on-warn secondary stack is part of the selected report but should not replace the root classification.

## State And Persistence
The persisted state is `TYPE: LOCKDEP`, `CORRUPTED: Y`, and `PANICKED: Y`. Runtime state includes failslab settings and panic-on-warn behavior.

## Dependencies And Integration Points
It depends on warning parsing, lockdep bug detection, corruption heuristics, panic-on-warn detection, and noisy fault-injection filtering.

## Risks
The parser can overfit to the tty/ioctl syscall path or panic frame and lose the lockdep classification.

## Test Signals
Stable parsing means title `WARNING: locking bug in corrupted`, type `LOCKDEP`, both flags set, and no selection of `lock_downgrade` as a clean non-corrupted title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/335 -->
