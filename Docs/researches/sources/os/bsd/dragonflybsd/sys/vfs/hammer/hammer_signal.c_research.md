# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_signal.c

Purpose: provides a small helper for interruptible long-running HAMMER ioctl operations such as prune, rebalance, reblock, and PFS rollback.

Behavior: `hammer_signal_check()` yields the current LWKT thread on every call, then checks for pending actionable user signals only once every 100 calls via `hmp->check_interrupt`. It uses `CURSIG_NOBLOCK(curthread->td_lwp)` so it does not block or stop the thread while polling.

Return contract: returns `0` when work should continue and `EINTR` when a signal is pending. Callers commonly translate `EINTR` into an ioctl header interrupt flag and return success to userland so administrative tools can resume or report partial progress.

Research notes: the helper is intentionally lightweight and mount-scoped. Its throttled check avoids excessive signal polling inside tight B-tree scans while still keeping maintenance ioctls responsive.
