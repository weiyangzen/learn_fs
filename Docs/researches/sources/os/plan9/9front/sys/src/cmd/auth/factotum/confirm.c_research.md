# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/confirm.c

Factotum support for `/mnt/factotum/confirm` and `/mnt/factotum/needkey` wait queues.

Key responsibilities:
- Queues RPC reads waiting for user confirmation of keys marked with `confirm`.
- Emits confirmation requests into a log-style buffer and accepts `tag`/`answer=yes|no` writes.
- Applies confirmation decisions back to the waiting `Fsstate`.
- Queues RPC reads that need new keys and emits `needkey tag=...` messages.
- Accepts needkey completion/error writes and resumes blocked RPC reads.
- Handles flush/interruption for both confirmation and needkey waiters.

Dependencies:
- Uses `Logbuf` helpers from `log.c`, factotum `Fsstate`, 9P `Req`, and RPC continuation helpers.

Notable risks:
- Confirmation and needkey code paths are parallel copies with separate queues and locks.
