# sources/test-tools/stress-ng/stress-poll.c

Purpose: `stress-poll.c` implements the `poll` stressor, using many pipes and a writer child to exercise `poll`, optional `ppoll`, `select`, and `pselect` with short or randomized timeouts.

Important APIs/types/functions: `pipe_fds_t` stores a pipe pair. `pipe_read()` reads a 16-bit pipe index token and verifies it when global verify is enabled. `stress_poll()` allocates pipe, pollfd, and randomized index arrays, creates pipes, forks a writer, and runs poll/select loops in the parent.

Control flow: the stressor resolves `poll-fds` and `poll-random-us`, allocates arrays, randomizes an index schedule, creates `max_fds` pipes, synchronizes, and forks. The child closes read ends and writes the pipe index as a token to randomly selected write ends. The parent prepares `pollfd` entries, intentionally sets one invalid fd to exercise `POLLNVAL`, and loops through `poll`, `ppoll`, invalid `ppoll` timeout, optional rlimit-lowered `ppoll`, `select`, `pselect`, and `sleep(0)`, draining ready pipes and incrementing bogo ops on readiness.

State and persistence behavior: state is heap arrays, pipe descriptors, a writer child, randomized index schedule, and optional temporary `RLIMIT_NOFILE` changes restored immediately. No files are created.

Dependencies and integration points: `poll.h`, optional select/pselect/ppoll, pipe I/O, rlimit, stress-ng affinity/scheduler/fork helpers, sync barriers, and `CLASS_SCHEDULER | CLASS_OS` registration with optional verification.

Risks: `select` and `pselect` only include fds below `FD_SETSIZE`; high pipe counts can reduce select coverage. The intentionally invalid fd should not make `poll()` fail but should set `POLLNVAL`. Writer child may hit pipe backpressure if readers cannot keep up.

Test signals: `--poll` should bogo-progress. Useful variants include `--poll-fds 1`, max fds, `--poll-random-us`, verify mode, systems without ppoll/pselect, and rlimit behavior for too many fds.
