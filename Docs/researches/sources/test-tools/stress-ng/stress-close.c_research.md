<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-close.c -->
# sources/test-tools/stress-ng/stress-close.c

## Purpose
Implements the `close` stressor, creating races between the main worker and helper pthreads that duplicate, close, range-close, and otherwise manipulate many file descriptors.

## Important APIs, Types, and Functions
`stress_close_info` registers the stressor with `close-fds`. Global volatile `fd`, `dupfd`, and `max_delay_us` coordinate intentionally racy close targets. `stress_close_func()` is the helper thread that dup2s stderr into high fd slots, closes shared fds, tests advisory locks, random bad closes, and `close_range`. `stress_close()` creates helper threads and cycles through many fd-producing APIs.

## Control Flow
The main function starts three pthreads, creates a temp file for `faccessat` invalid-dirfd checks, synchronizes, then repeatedly opens a random fd source: sockets, `/dev/zero`, tmpfile, epoll, eventfd, fanotify, inotify, pipe, signalfd, userfaultfd, O_PATH, directory, shm, bad fd, proc fd, or stdin. It duplicates, probes ownership/access/stat paths, closes the fd while helpers race, verifies a second close fails with EBADF or EINTR, updates timing, and adjusts helper delay.

## State and Persistence Behavior
State is in-process and temporary: pthreads, shared volatile fd variables, optional POSIX shm name, a temporary file directory, and many short-lived file descriptors. Cleanup joins threads, closes temp fd, and removes the temp directory. No persistent files should remain.

## Dependencies and Integration Points
Depends on pthreads, stress-ng pthread wrappers, capability checks, bad-fd helpers, close_range shim, many optional Linux fd APIs, sockets, temp filesystem helpers, metrics, and signal mask handling. It registers an unimplemented stressor without pthread support.

## Risks and Edge Cases
The stressor intentionally races close operations, so fd reuse can make failures timing-sensitive. Some fd source APIs require kernel support or privileges and may fail. `close_range` flags vary. The second-close verification must tolerate EINTR. Threads block signals so the controlling thread handles termination.

## Test Signals
Expected signals include no "unexpectedly able to close the same file twice" failures, nonzero close-rate metric, clean pthread joins, and cleanup of temp files. Exercise low and high `--close-fds` values.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-close.c -->
