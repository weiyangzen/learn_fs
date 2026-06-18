# sources/test-tools/liburing/test/pollfree.c

Purpose: stress-tests pollfree wakeups when tasks exit with outstanding signalfd reads submitted through io_uring. It repeatedly forks children that create a ring, arm multiple reads on a nonblocking `signalfd`, then exit without explicitly waiting for completions, provoking cleanup paths for poll waiters.

Important APIs and types: `signalfd`, `sigemptyset`, `sigaddset`, `io_uring_prep_read`, `IOSQE_ASYNC`, `fork`, `waitpid`, `gettimeofday`, and `mtime_since_now`. Ring setup flags tested are plain, `IORING_SETUP_SQPOLL`, `IORING_SETUP_COOP_TASKRUN`, and `IORING_SETUP_DEFER_TASKRUN|IORING_SETUP_SINGLE_ISSUER`.

Control flow: `child()` initializes a ring, creates a nonblocking signalfd for `SIGINT`, submits three reads with different `user_data`, marks the middle read `IOSQE_ASYNC`, and exits. `run_test()` forks and waits. `test()` loops for roughly 2.5 seconds per flag set, stopping early if signalfd is unavailable. `main()` runs plain mode first, then SQPOLL, cooperative task-run, and deferred task-run variants.

State and persistence: `no_signalfd` is a process-global feature flag. A static `index` in the child throttles every eighth iteration with a short sleep, increasing scheduling variety. Outstanding requests persist only until child process teardown, which is the cleanup path being exercised.

Dependencies and integration: requires Linux signalfd and io_uring support for the selected setup flags. `-EINVAL` ring setup for a mode is treated as unsupported by returning success from the child.

Risks and test signals: kernel bugs may show up as child failures, hangs, or missed cleanup wakeups. The test does not inspect CQEs; its signal is absence of failures across repeated process-exit cleanup under all supported modes.
