# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mutex_emul.c

Single-thread mutex emulation/debug checker.

Key behavior:
- Tracks magic value, owner string, held count, and source location.
- `eMmutex_enter()` aborts if uninitialized or already held.
- `eMmutex_exit()` aborts if not held exactly once.
- Init/destroy maintain a global `initcount`; `ipf_mutex_clean()` aborts if locks remain.

Research notes:
- This is not a real blocking mutex; it is misuse detection for userland/emulated builds.
