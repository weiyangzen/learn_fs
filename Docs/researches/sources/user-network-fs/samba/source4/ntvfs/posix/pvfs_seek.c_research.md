# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_seek.c

Purpose: `pvfs_seek.c` implements SMB seek semantics for open PVFS file handles. It updates the handle's logical seek offset and returns the resulting value.

Important APIs, types, and functions: The only exported function is `pvfs_seek`. It uses `union smb_seek`, `struct pvfs_file`, and `struct pvfs_file_handle`, with `SEEK_MODE_START`, `SEEK_MODE_CURRENT`, and `SEEK_MODE_END`.

Control flow: `pvfs_seek` finds the backend handle through `pvfs_find_fd` and returns `NT_STATUS_INVALID_HANDLE` if absent. For start-relative seeks it assigns the requested offset. For current-relative seeks it adds the requested offset to `h->seek_offset`. For end-relative seeks it refreshes metadata with `pvfs_resolve_name_fd(..., PVFS_RESOLVE_NO_OPENDB)` and sets the offset to current file size plus the requested offset. The resulting offset is returned in `io->lseek.out.offset`.

State and persistence behavior: The function mutates only `h->seek_offset`; it does not call POSIX `lseek` and does not affect durable file contents or xattrs. End-relative seeks refresh the handle's `pvfs_filename` stat/DOS state.

Dependencies and integration points: It depends on open handle lookup and `pvfs_resolve_name_fd`. Read and write paths independently update `position` and `seek_offset`; this function is part of that handle-local position model.

Risks: The code does not reject unknown seek modes explicitly, leaving the default `NT_STATUS_OK` and previous offset unchanged. It does not validate overflow or negative results after unsigned arithmetic. End-relative seek on a directory fd of `-1` still uses path stat through `pvfs_resolve_name_fd`.

Test signals: Cover invalid handles, all three modes, end-relative seek after external size changes, unknown mode behavior, large offset arithmetic, and interaction with subsequent read/write position reporting.
