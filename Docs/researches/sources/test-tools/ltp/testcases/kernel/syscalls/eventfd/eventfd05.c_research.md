# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd05.c

Purpose: Checks that eventfd descriptors shared across `fork()` expose child counter updates to the parent.

Important APIs/types/functions: `eventfd`, `SAFE_FORK`, `SAFE_WRITE`, `tst_reap_children`, `SAFE_READ`, and `.forks_child = 1`.

Control flow: The parent creates a nonblocking eventfd, the child writes `0xdeadbeef` and exits, the parent reaps the child, reads the counter, and compares the returned value.

State and persistence behavior: The kernel eventfd object persists across fork through the inherited open file description; no durable storage is used.

Dependencies and integration points: Uses LTP fork management and `CONFIG_EVENTFD`; the expected behavior comes from file descriptor inheritance.

Risks and test signals: Failures indicate broken fork inheritance, eventfd counter sharing, or child write/read ordering. Reaping before the read removes scheduling races.
