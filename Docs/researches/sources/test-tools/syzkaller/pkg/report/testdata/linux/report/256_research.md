<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/256 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/256

## Purpose
This fixture verifies NULL pointer dereference parsing in the socket polling path. The expected title is `BUG: unable to handle kernel NULL pointer dereference in sock_poll`, alt `bad-access in sock_poll`, type `NULL-POINTER-DEREFERENCE`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The raw log is a KASAN-enabled oops with `BUG: unable to handle kernel NULL pointer dereference at 0000000000000000`. Parser pieces include page-fault matching, stack frame extraction, bad-access alternate generation, panic detection, and crash type mapping. Key symbols include `smc_poll`, `ep_insert`, `__x64_sys_epoll_ctl`, `sock_poll`, `vfs_poll`, `ep_item_poll.isra.15`, `__mutex_lock`, and `do_syscall_64`.

## Control Flow
The reporter must handle a null `RIP`, stack data, call trace, module/end-trace lines, and a final fatal-exception panic. The meaningful title frame is `sock_poll`, even though `smc_poll` and epoll allocation frames appear around it.

## State and Persistence Behavior
No state is mutated. Persistent expected state is title, alt title, null-deref type, and panic flag.

## Dependencies and Integration Points
It depends on Linux oops regexes, stack parsing, KASAN/noise tolerance, and `crash.TitleToType`.

## Risks and Edge Cases
The parser could select `smc_poll` or an epoll helper if frame scoring changes. The repeated RIP/user-register sections must not create a second report.

## Test Signals
Success is stable `sock_poll` title and alt, `NULL-POINTER-DEREFERENCE`, and panic flag true.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/256 -->
