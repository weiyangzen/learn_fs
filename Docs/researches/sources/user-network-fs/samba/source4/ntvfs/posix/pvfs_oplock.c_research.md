# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_oplock.c

Purpose: `pvfs_oplock.c` handles opportunistic-lock state for open PVFS files. It registers local recipients for open-db oplock break messages, forwards breaks to SMB clients, updates the open database when clients release or downgrade oplocks, and asks the open database to break level-II oplocks before writes.

Important APIs, types, and functions: The central local type is `struct pvfs_oplock`, which tracks the owning `pvfs_file_handle`, the `pvfs_file` needed for client callbacks, the current oplock level, first-break timestamps, and the messaging context. Public functions are `pvfs_setup_oplock`, `pvfs_oplock_release`, and `pvfs_break_level2_oplocks`. Key helpers are `pvfs_oplock_release_internal`, `pvfs_oplock_break`, `pvfs_oplock_break_dispatch`, and the destructor that deregisters `MSG_NTVFS_OPLOCK_BREAK`.

Control flow: `pvfs_setup_oplock` translates open-db return values into internal levels, allocates an oplock object under the file handle, and registers an imessaging callback. When a break message arrives, `pvfs_oplock_break_dispatch` validates payload length, ignores messages for other file handles, and calls `pvfs_oplock_break`. The break handler sends `ntvfs_send_oplock_break` once per target level, suppresses duplicate sends until the configured timeout, then auto-releases through `pvfs_oplock_release_internal`. Client lock requests call `pvfs_oplock_release`, extract the break level from the lock mode, and update open-db state.

State and persistence behavior: Runtime oplock state is attached to `h->oplock`; durable/interprocess visibility is in the open database via `odb_update_oplock` and `odb_break_oplocks`. If a break reaches none, the local oplock object is freed. Break timestamps prevent repeated client notifications before timeout.

Dependencies and integration points: This file depends on the open database, imessaging, ntvfs oplock-break delivery, tevent time helpers, and `pvfs_open.c` handle state. `pvfs_write.c`, `pvfs_setfileinfo.c`, and open handling call into it before operations that invalidate level-II caching.

Risks: Pointer identity in the message payload is process-local coordination and must match the open-db sender's assumptions. Failure paths return `NT_STATUS_FOOBAR` in several internal-error cases, which is imprecise. Auto-release after timeout trades client correctness for server progress. Message registration lifetime must match handle lifetime.

Test signals: Exercise exclusive, batch, and level-II grants; break-to-level-II and break-to-none; duplicate break suppression; timeout auto-release; client release via LOCKX; write-triggered level-II breaks; and cleanup on handle close.
