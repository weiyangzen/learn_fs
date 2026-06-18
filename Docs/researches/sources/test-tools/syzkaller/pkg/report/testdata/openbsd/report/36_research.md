# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/36

Purpose: OpenBSD protection fault fixture with source-line-rich stack. Expected title is `protection_fault: ktrops`.

Important parser APIs and patterns: handled by the `kernel:` oops group rule `kernel: protection fault trap, code=0.*\\nStopped at[ ]+([^\\+]+)` formatted as `protection_fault: %[1]v`. Symbolization frame regexes consume `at function+0xoffset` lines and inline source annotations.

Control flow: a login-prefixed `kernel: protection fault trap` stops at `ktrops+0x4a`. DDB trace shows `ktrops`, `doktrace`, `sys_ktrace`, `syscall`, and `Xsyscall`, with inline references to `sys/kern/kern_ktrace.c`. Additional process, lock, malloc, and per-CPU traces follow.

State and persistence: static crash fixture retaining register values; the `rbx`/`r12` poison value `0xdead4110dead4110` is significant diagnostic context but not title material.

Dependencies and integration: tests OpenBSD protection-fault title extraction, CR/prompt tolerance, source-line stack preservation, and multi-CPU DDB output.

Risks: page-fault and protection-fault formats are similar; mixing them would misclassify this crash. The title must use `ktrops`, not later CPU-0 `kqueue_scan`.

Test signals: exact title `protection_fault: ktrops`; primary stack includes `sys_ktrace`.
