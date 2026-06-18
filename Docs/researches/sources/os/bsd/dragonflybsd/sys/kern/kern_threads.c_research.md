# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_threads.c

Tiny syscall implementation file for the general-purpose user yield system call.

Key API:
- `sys_yield()`

Behavior:
- Sets `sysmsg->sysmsg_result` to `0`.
- Calls `lwkt_user_yield()` to yield the current user thread.
- Returns success.

Concurrency model:
- Marked MPSAFE.
- No local locks or complex state.

Filesystem relevance:
- No direct filesystem logic. It is scheduler plumbing that can influence latency and fairness for filesystem-using user processes.
