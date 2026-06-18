<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/246 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/246

## Purpose
This is a second large stack-unwinder fixture for the same normalized syzkaller title, `WARNING: kernel stack regs has bad value`. It provides a 1061-line variant with different surrounding kernel work, networking, and syscall frames so the no-stack-trace warning rule is not overfit to report 245.

## Important APIs, Types, and Functions
The data contract is the same `ParseTest` header/log format with a single `TITLE`. Parser paths include `Reporter.Parse`, Linux oops signature scanning, title normalization, and printk-prefix cleanup. Representative kernel symbols in the noise include `keccakf`, `rcu_is_watching`, `nf_hook_slow`, `ip_rcv`, `fd_install`, `__sys_accept4`, `__x64_sys_sendto`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control Flow
`parseReport` reads the expected header, then the Linux reporter scans the raw log until it reaches the two terminal warnings: one for a bad frame pointer and one for bad `bp` stack regs. The intended parser control flow is to classify either spelling through the same no-stack-trace oops rule and emit the stable generic title.

## State and Persistence Behavior
The file persists a different raw kernel trace variant, including sanitized pointer values and networking/syscall frames, but it owns no runtime state. Expected state is the canonical title only; no `TYPE`, `PANICKED`, `CORRUPTED`, or explicit `REPORT` block is stored.

## Dependencies and Integration Points
It depends on the Linux report regex catalog, especially the stack-regs and stack-frame-pointer warning patterns, and on the generic test harness comparison of parsed fields. Integration is through the syzkaller Linux report testdata directory.

## Risks and Edge Cases
Because the actual warning is at EOF, parser truncation, scanner limits, or early false positives would regress this fixture. The file also checks that irrelevant NMI, RCU, lockdep, and syscall-looking entries do not become the selected title.

## Test Signals
Success means the parsed title remains `WARNING: kernel stack regs has bad value` and the report bounds include the terminal stack-register warning rather than the preceding function dump.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/246 -->
