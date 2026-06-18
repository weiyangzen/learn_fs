# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/24

Purpose: OpenBSD kqueue invariant panic fixture. Expected title is `kqueue: knote !ACTIVE`.

Important parser APIs and patterns: `openbsdOopses` includes `panic: (kqueue|knote).* ([a-z]+ .*)` formatted as `kqueue: %[2]v`. This fixture proves that the reporter extracts the semantic invariant (`knote !ACTIVE`) from a panic line containing addresses and source line data.

Control flow: the panic begins in `kqueue_scan:879`, enters DDB on CPU 1, and the primary stack runs through `kqueue_do_check`, `kqueue_scan`, `sys_kevent`, `syscall`, and `Xsyscall`. Later DDB sections include registers, process state, locks, and allocator tables.

State and persistence: the fixture is static, but encodes concurrent executor state with multiple TIDs/CPUs and a concrete kqueue/knote pair. Those details exercise noise tolerance rather than persistent application state.

Dependencies and integration: covers the OpenBSD reporter’s kqueue/knote title formatter and BSD stack parsing. It interacts with shared title sanitization to ignore hex addresses and line numbers.

Risks: regex greediness could capture too much from `kqueue_scan:879: kq=... kn=... knote !ACTIVE`, or fail if future OpenBSD messages reorder fields. Multi-CPU DDB prompts can also affect boundaries.

Test signals: exact title `kqueue: knote !ACTIVE`; key frames are `kqueue_do_check`, `kqueue_scan`, and `sys_kevent`.
