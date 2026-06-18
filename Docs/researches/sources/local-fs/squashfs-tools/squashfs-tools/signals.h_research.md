# File Research: sources/local-fs/squashfs-tools/squashfs-tools/signals.h

Provides inline `wait_for_signal(sigset_t *sigmask, int *waiting)` abstraction. macOS/OpenBSD use plain `sigwait()` and clear `waiting`.

Other platforms use `sigtimedwait()` while `*waiting` is true, falling back to blocking `sigwaitinfo()` after timeout. `EAGAIN` clears waiting, `EINTR` retries, and other errors call `BAD_ERROR()`.

This lets callers periodically leave a “waiting” state while still handling signals portably.
