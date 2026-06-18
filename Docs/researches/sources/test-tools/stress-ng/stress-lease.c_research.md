# sources/test-tools/stress-ng/stress-lease.c

Purpose: implements `lease`, a filesystem lease stressor that alternates read and write leases while child breaker processes attempt nonblocking opens to trigger lease-break notifications.

Important APIs/types/functions: `lease_sigio` counts `SIGIO` signals. `stress_lease_handler()` increments it. `stress_lease_spawn()` creates breaker children. `stress_try_lease()` opens the file, loops until `F_SETLEASE` succeeds, reads current lease with `F_GETLEASE`, increments bogo ops, then unlocks with `F_UNLCK`.

Control flow: `stress_lease()` resolves `lease-breakers`, installs the SIGIO handler, creates a temp file, spawns breaker children, sync-starts, and loops through write-lease and read-lease attempts. Breaker children repeatedly open the same file with `O_NONBLOCK | O_WRONLY`, tolerating `EWOULDBLOCK` and `EACCES`, then query the lease and close. Teardown kills all breakers, unlinks the file, removes the temp directory, and records SIGIO interrupts per second.

State and persistence behavior: temporary file and directory are removed at exit. Runtime state includes active kernel leases, child processes, signal count, and open fds.

Dependencies and integration points: compile-gated on `F_SETLEASE`, `F_WRLCK`, and `F_UNLCK`. Uses stress-ng temp files, process state, fork retry, scheduler settings, kill helpers, and metrics. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: lease semantics are Linux/filesystem-specific and may require permission or local filesystem support. Unlock loops can spin on `EAGAIN`. Signal delivery is asynchronous, and `lease_sigio` is a plain `uint64_t` updated from a handler.

Test signals: vary breaker counts, run on filesystems with and without lease support, ensure breaker children are reaped, temp files removed, bogo ops advance, and SIGIO metric is plausible.
