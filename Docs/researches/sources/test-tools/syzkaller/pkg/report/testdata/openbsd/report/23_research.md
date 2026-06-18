# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/23

Purpose: OpenBSD fixture for a packet-filter address-family panic. Expected title is `panic: unhandled af`; expected crash type is `DoS`.

Important parser APIs and patterns: handled by `openbsdOopses` under the `panic:` group, specifically `panic: unhandled af`, formatted without the numeric family value. `Reporter.ParseFrom` later sanitizes dynamic values and assigns `crash.Type` from the test metadata.

Control flow: the log records `panic: unhandled af 1`, DDB entry, process table row for `syz-executor6559`, and a stack through `unhandled_af`, `pf_addrcpy`, `pfioctl`, `VOP_IOCTL`, `vn_ioctl`, `sys_ioctl`, `syscall`, and `Xsyscall`. The repeated `show panic` and `trace` output confirms the panic line and stack after DDB prompt handling.

State and persistence: no mutable program state exists in this fixture. The file persists representative OpenBSD kernel state such as process IDs, register dump, and pool statistics.

Dependencies and integration: tests OpenBSD-specific panic title compaction and syzkaller’s generic dynamic-title replacement. It also validates that network/pf ioctl crashes are grouped under the stable `unhandled af` title.

Risks: if the parser captured the numeric address family, deduplication would fragment. The long trailing diagnostics also stress report-end heuristics.

Test signals: expected title `panic: unhandled af`, expected `TYPE: DoS`, and stack frame signal `unhandled_af` reached from `pfioctl`.
