# sources/test-tools/ltp/testcases/kernel/fs/doio/forker.c

Purpose: `forker.c` supplies process fan-out helpers used by filesystem stress programs. `background()` detaches the caller by forking and letting the parent exit. `forker()` creates a requested number of copies of the current process using either a flat parent-with-many-children shape or a chained child-of-child shape.

Important APIs and types: exported globals are `Forker_pids[FORKER_MAX_PIDS]` and `Forker_npids`. Public functions are `background(char *prefix)` and `forker(int ncopies, int mode, char *prefix)`. The file uses `fork()`, `getpid()`, `exit()`, and stderr diagnostics with `errno`/`strerror()`. A `UNIT_TEST` main can be compiled to exercise both helpers manually.

Control flow: `background()` calls `fork()`: failure prints an optional prefixed message and exits with `errno`; the parent exits zero; the child returns zero. `forker()` loops from one to `ncopies - 1`. In mode 1, each process forks one child; the parent returns immediately and only the child continues the loop. In default mode, the original parent keeps forking and each child returns immediately. Each successful fork increments `Forker_npids` and stores either the child pid or current child pid while capacity remains.

State and persistence behavior: pid state is process-local after forks. Different processes see different snapshots of `Forker_pids`; comments explicitly warn that only some processes know all child pids depending on mode. The fixed array stores at most `FORKER_MAX_PIDS` entries, while `Forker_npids` can continue to grow past the number of stored pids. `background()` intentionally orphans the continuing child.

Dependencies and integration points: `growfiles.c` uses `background()` for default asynchronous launch and `forker()` for `-n` multiple-copy stress. `notify_others()` in `growfiles.c` uses `Forker_pids` and `Forker_npids` to propagate `SIGUSR2` when synchronized stopping is requested. `forker.h` declares the shared interface.

Risks: there is no wait/reap logic here, so callers must own process lifecycle. The fixed pid array can truncate stored pids for very high copy counts. Return values differ by process and mode, so callers must not interpret them as a single global count without understanding the topology. Failure returns can be partial and do not clean up already-forked children.

Test signals: useful signals include expected process counts in flat and chained modes, parent exit after `background()`, correct pid array population for small `ncopies`, graceful failure on fork limits, and successful signal fan-out from callers that rely on `Forker_pids`.
