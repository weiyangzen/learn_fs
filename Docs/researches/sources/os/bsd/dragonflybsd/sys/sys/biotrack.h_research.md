# File Research: sources/os/bsd/dragonflybsd/sys/sys/biotrack.h

Read completely: 26 lines.

This header defines a minimal in-progress BIO tracking counter.

Key contents:
- `struct bio_track` with active I/O count.
- Macros to read and increment the active count.
- Kernel prototype `bio_track_wait()` for waiting on tracked I/O completion.

Security/reliability notes:
- Very small synchronization surface. Correctness depends on paired decrement/wakeup behavior in the implementation outside this header.
