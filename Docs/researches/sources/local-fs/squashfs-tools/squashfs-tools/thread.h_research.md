# File Research: sources/local-fs/squashfs-tools/squashfs-tools/thread.h

This header exposes thread accounting types and functions used by compression/reader code.

Key contents:
- `struct thread` with `type` and `state`.
- Thread type constants: `THREAD_BLOCK`, `THREAD_FRAGMENT`.
- State constants: `THREAD_ACTIVE`, `THREAD_IDLE`.
- Overcommit defaults/stringification macros.
- Extern `pthread_mutex_t thread_mutex`.
- Public functions for id allocation, idle transitions, waiting, dumping state, and configuring overcommit.

Important behavior:
- Callers coordinate via the exported `thread_mutex`.
- The overcommit default is `0%`, meaning fragment throttling defaults to at most the processor count unless configured otherwise.
