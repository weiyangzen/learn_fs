# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/449

Purpose: golden fixture for KCSAN race report parsing. Expected title is `KCSAN: data-race in netlink_recvmsg / netlink_recvmsg`, type is `KCSAN-DATARACE`, and `PANICKED: Y`.

Important APIs, types, and functions: the fixture uses the optional `REPORT:` block path in `parseReport`, so `ParseTest.HasReport` and normalized `Report` comparison are important. Kernel frames include two racing `netlink_recvmsg` accesses, `sock_recvmsg_nosec`, `___sys_recvmsg`, `do_recvmmsg`, `sock_recvmsg`, `__sys_recvfrom`, `kcsan_report`, `kcsan_setup_watchpoint`, and `__tsan_unaligned_write2`.

Control flow: the log contains the raw KCSAN report, then panic-on-warn stack text, then an explicit normalized `REPORT:` block. The parser must detect KCSAN as the crash, set the panicked flag from the later panic, and return a report body matching the normalized block rather than including the panic tail.

State and persistence behavior: static data stores both raw console output and expected normalized report body. There is no mutable state, but this fixture persists a dual-section oracle for report extraction.

Dependencies and integration points: depends on KCSAN-specific Linux oops matchers, normalized report extraction, and the test harness' `REPORT:` comparison. It integrates netlink receive paths and KCSAN sanitizer output.

Risks: if the parser includes the panic stack in the report body, `HasReport` comparison fails. If the title normalizer loses the two-function race format, deduplication across KCSAN reports degrades.

Test signals: `BUG: KCSAN: data-race in netlink_recvmsg / netlink_recvmsg`, two write stacks to the same address, `Reported by Kernel Concurrency Sanitizer`, panic-on-warn, and explicit `REPORT:` block.
