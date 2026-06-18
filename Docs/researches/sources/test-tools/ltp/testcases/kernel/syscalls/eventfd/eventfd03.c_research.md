# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd03.c

Purpose: Verifies `select()` read readiness for an eventfd follows the counter being nonzero versus zero.

Important APIs/types/functions: `eventfd`, `fd_set`, `FD_ZERO`, `FD_SET`, `FD_ISSET`, `select()`, zero-timeout `timeval`, `SAFE_WRITE`, and `SAFE_READ`.

Control flow: After creating a nonblocking eventfd, the test writes 10, calls `select()` with the descriptor in the read set and expects readiness, drains the counter, calls `select()` again, and expects the descriptor not to be set.

State and persistence behavior: State is the eventfd counter. A write makes it readable; a full 8-byte read resets the counter to zero and removes read readiness.

Dependencies and integration points: Integrated with LTP result macros and `CONFIG_EVENTFD`; it relies on normal `select()` fdset mutation semantics.

Risks and test signals: The same `fd_set` is reused after `select()`, so the test depends on the previous ready bit still being present until the second call clears it. Failures show as wrong readiness or `select()` errors.
