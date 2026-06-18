<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/247 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/247

## Purpose
This fixture verifies NULL program-counter oops parsing for an IPv4 send path crash. The expected title is `BUG: unable to handle kernel NULL pointer dereference in inet_sendmsg`, with alternate `bad-access in inet_sendmsg`, type `NULL-POINTER-DEREFERENCE`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The source uses `TITLE`, `ALT`, `TYPE`, and `PANICKED` headers. Parser code under test includes Linux page-fault/oops matchers, frame extraction, crash type mapping, and panic detection. Kernel frames include `inet_autobind`, `inet_sendmsg`, `sock_sendmsg`, `___sys_sendmsg`, `__sys_sendmsg`, `SyS_sendmsg`, and `system_call_fastpath`.

## Control Flow
The reporter encounters `BUG: unable to handle kernel NULL pointer dereference at (null)`, a null `RIP`, register dump, stack, and call trace. Because the raw instruction pointer is null, the parser must walk the call trace and choose `inet_sendmsg` as the meaningful frame, then notice the later `Kernel panic - not syncing: Fatal exception`.

## State and Persistence Behavior
The file has no mutable state. Persistent expected state is the normalized title, alternate bad-access title, crash type, and panic flag. Dynamic machine names, task pointers, and trace ids are retained only as raw fixture input.

## Dependencies and Integration Points
It depends on Linux oops parsing, bad-access title generation, `crash.TitleToType`, panic-line detection, and `TestParse` field comparison.

## Risks and Edge Cases
The null `RIP` and `Code: Bad RIP value` lines are not useful frames; using them directly would produce an empty or `(null)` title. Secondary lockdep helper frames must not displace `inet_sendmsg`.

## Test Signals
Regression checks are stable title, type `NULL-POINTER-DEREFERENCE`, alt title `bad-access in inet_sendmsg`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/247 -->
