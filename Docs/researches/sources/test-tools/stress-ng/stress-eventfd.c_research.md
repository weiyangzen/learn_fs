# sources/test-tools/stress-ng/stress-eventfd.c

Purpose: implements `eventfd`, stressing Linux eventfd counters with bidirectional parent/child read-write traffic, optional nonblocking mode, fdinfo reads, and invalid read/write coverage.

Important APIs/types/functions: option `eventfd-nonblock` controls `EFD_NONBLOCK`. `stress_eventfd()` creates two eventfds, forks a child, coordinates ping-pong writes and reads, and validates full `uint64_t` transfers. It also tests invalid `eventfd(0, ~0)` and small-buffer/overflow writes.

Control flow: after creating `fd1` and `fd2` with `EFD_CLOEXEC`, `EFD_SEMAPHORE`, and optional `EFD_NONBLOCK`, the parent sync-starts and forks. The child is pinned near the parent CPU, applies stress-ng child settings, repeatedly reads from `fd1`, periodically attempts invalid small or all-ones writes, then writes `1` to `fd2`. The parent reads eventfd proc fdinfo, writes `1` to `fd1`, reads from `fd2`, and increments bogo operations. Both sides retry `EAGAIN` and `EINTR`.

State and persistence behavior: state is entirely kernel eventfd counters and process-local loop variables. No files are created except transient `/proc/self/fdinfo` reads. Cleanup kills the child and closes both fds.

Dependencies and integration points: gated by `sys/eventfd.h`, `eventfd()`, and glibc 2.8. Uses stress-ng affinity, killpid, fdinfo, scheduler, sync, process-state, and filesystem-usage accounting helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: nonblocking mode can spin on `EAGAIN`; semaphore mode changes read decrement semantics but still works for single-token ping-pong. Short writes/reads are intentionally invalid and must not be treated as failures unless valid 8-byte operations are short. Fork failure handling retries through stress-ng helpers.

Test signals: run blocking and `--eventfd-nonblock` modes with `--verify`, inspect for short read/write failures, confirm child cleanup, and check eventfd fdinfo paths are exercised without requiring persistent files.
