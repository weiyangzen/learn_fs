# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_write.c

Purpose: `pvfs_write.c` implements SMB write handling for PVFS files and streams, including access checks, byte-range-lock checks, level-II oplock breaks, delayed write-time updates, and POSIX or stream writes.

Important APIs, types, and functions: The exported function is `pvfs_write`. Local helpers are `pvfs_write_time_update_handler` and `pvfs_trigger_write_time_update`. It uses `union smb_write`, `struct pvfs_file`, `struct pvfs_file_handle`, open-db locks, tevent timers, and either POSIX `pwrite` or `pvfs_stream_write`.

Control flow: Non-WRITEX levels are delegated to `ntvfs_map_write`. WRITEX finds the open handle, rejects directory handles, verifies write or append access, checks byte-range locks, breaks level-II oplocks, schedules a delayed open-db write-time update if not already triggered, then writes to the stream blob or POSIX fd. `EFBIG` maps to `NT_STATUS_INVALID_PARAMETER`; other errors use PVFS errno mapping. Successful writes update `seek_offset` and return the written byte count.

State and persistence behavior: Data is persisted through POSIX file contents or stream xattr/EADB blobs. Write-time state is persisted first in the open database by a delayed timer, then potentially to filesystem timestamps on close. The timer sets `update_triggered` and `update_on_close`, and the handler calls `odb_set_write_time` with the timer time.

Dependencies and integration points: It depends on open handle lookup, byte-range lock enforcement, oplock breaking, open-db write-time fields, stream storage, POSIX pwrite, and tevent.

Risks: Delayed write-time updates rely on timer delivery and close-path fallback. Stream writes load and rewrite blobs, so large writes are memory- and xattr-limit-sensitive. Append access is accepted but the code writes at the supplied offset, so append semantics depend on earlier generic mapping or clients.

Test signals: Cover write access denial, append-only handles, locked ranges, level-II oplock break failures, delayed write-time update and close fallback, stream writes including sparse extension, EFBIG mapping, and short writes/errors.
