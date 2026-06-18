# sources/user-network-fs/samba/source3/smbd/durable.c

## Purpose
`durable.c` implements the default VFS durable handle cookie, disconnect, and reconnect logic. It serializes enough file/open/stat state to let an SMB durable handle survive a clean disconnect, then validates and reopens it only if share-mode and filesystem state prove the file was not changed by another opener.

## Important APIs, types, and functions
- `vfs_default_durable_cookie()` creates an NDR `vfs_default_durable_cookie` with file ID, service path, base name, allocation size, file position, write-time-forced flag, and stat data.
- `vfs_default_durable_disconnect()` validates the old cookie, marks share mode and byte-range locks disconnected, stats the file, builds a reconnectable cookie, and closes the fd.
- `vfs_default_durable_reconnect()` decodes the cookie, converts the stored name to a dirfsp-relative path, creates a new FSP, and calls `share_mode_do_locked_brl()`.
- `vfs_default_durable_reconnect_fn()` finds the unique disconnected share-mode entry, restores FSP open state/lease/locks, opens the file, checks stat/file ID, restores oplock, and creates a fresh cookie.
- `vfs_default_durable_reconnect_check_stat()` compares cookie stat fields to current stat fields.

## Control flow
Cookie creation refuses unsupported situations: disabled durable handles, kernel share modes/oplocks, POSIX locks, directories, streams, and fake files. Disconnect requires handle leases, supported lock/write conditions, no delete-on-close, valid regular-file stat, and successful share-mode/BRL disconnected marking. Reconnect requires durable handles enabled, cookie magic/version/allow flag, same share path, same file ID, a unique disconnected share-mode entry matching the persistent open ID, compatible write access, matching client GUID for leases, BRL reconnection, successful fd reopen, stat equality, and successful oplock restoration.

## State and persistence behavior
Durable state persists in SMBX open records and share-mode/byte-range lock databases, with the VFS cookie stored as an opaque blob in the open record. Disconnect closes the local fd but leaves durable open state for scavenging/reconnect. Reconnect mutates the share-mode entry from disconnected server ID to current server ID/MID and reattaches the `smbXsrv_open` to a new `files_struct`.

## Dependencies and integration points
The file depends on generated NDR open-files structures, share-mode and BRL APIs, leases database, server ID disconnected markers, `fd_openat()`/`fd_close()`, `fdos_mode()`, fake-file detection, loadparm durable/kernel settings, and SMB request chain FSP fields. `close.c` invokes durable disconnect on shutdown close.

## Risks and edge cases
- Durable reconnect is intentionally conservative; any stat mismatch denies reconnect to avoid missed oplock breaks.
- Multiple matching disconnected share entries invalidate reconnect.
- Reconnect failure after share-mode reset deletes the share-mode entry to avoid corrupted state.
- The disconnect cookie stores `base_name = fsp_str_dbg(fsp)` in the shown code; reviewers should confirm this is always a valid reopen path, not just a debug string.
- Durable handles are incompatible with several kernel/stream/directory/delete-on-close scenarios.

## Test signals
Tests should cover successful durable disconnect/reconnect, cookie magic/version/servicepath/file ID failures, stat mismatch denial, duplicate share-mode entry denial, write access changed denial, lease GUID mismatch, BRL reconnect, POSIX lock rejection, stream/directory/fake-file rejection, and scavenger cleanup after disconnect.
