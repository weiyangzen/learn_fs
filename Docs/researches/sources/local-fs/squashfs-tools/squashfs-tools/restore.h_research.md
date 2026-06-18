# File Research: sources/local-fs/squashfs-tools/squashfs-tools/restore.h

Public header for recovery thread initialization.

Exports:
- `init_restore_thread()`

Role:
- Allows main setup code to start the signal-waiting restore thread for recovery-capable operations.

Notes:
- Return type is `pthread_t *`, so including code needs pthread declarations visible.
