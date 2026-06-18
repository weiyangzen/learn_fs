# sources/test-tools/stress-ng/stress-dup.c

Purpose: implements `dup`, which stresses file descriptor duplication and closure through `dup`, `dup2`, `dup3`, and `fcntl(F_DUPFD)`, with an optional Linux race reproducer for `dup2`/open `EBUSY`.

Important APIs/types/functions: `info_t` stores race context in shared mmap, including fd targets, FIFO path, clone pid, counts, and clone stack. `stress_dup2_race_clone()` shares the fd table and races `dup2()` against a blocking FIFO open. `static_dup2_child()` sets a short interval timer and manages the clone. `stress_dup2_race()` isolates the race in a forked process. `stress_dup()` performs the main fd duplication loops and metrics.

Control flow: the stressor maps race context and creates a temp directory when supported, opens `/dev/zero`, synchronizes start, and loops filling a static fd array up to the process file limit capped at 65536. For each fd it performs valid and invalid dup/dup3/dup2 operations, same-fd `dup2` verification, optional `F_DUPFD`, optional race pass, and bogo increment. It then closes the opened range and repeats.

State and persistence behavior: fd state is process-local in `fds[]`; race counts live in shared anonymous mmap and are logged at cleanup. A FIFO is created under the stress-ng temp directory for the race and removed on tidy. Metrics record total dup calls and average nanoseconds per dup call.

Dependencies and integration points: depends on stress-ng fd-limit, bad-fd, mmap, killpid, temp, timing, and metrics helpers. Race path requires Linux `clone`, `mkfifo`, `CLONE_VM`, and `CLONE_FILES`. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: high file limits can create many descriptors; cleanup through `stress_fs_close_fds()` is critical. Race code intentionally shares fd tables and uses timers/signals, so it is Linux-specific and isolated in a child to protect the parent. `dup3` availability is detected through `ENOSYS` fallback.

Test signals: run with low/high `ulimit -n`, verify metrics are emitted, no fd leaks occur, same-fd `dup2` failures are reported, and Linux builds log race attempts without wedging on FIFO open.
