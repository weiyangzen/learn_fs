# File Research: sources/os/linux/linux/fs/smb/server/oplock.h

This header defines ksmbd’s oplock/lease data structures, state constants, and public oplock API.

Constants:
- `OPLOCK_WAIT_TIME` is 35 seconds.
- Oplock object states: none, acknowledgement wait, and closing.
- Break transition flags describe write-to-read, read-handle-to-read, write-to-none, and read-to-none.

Key structures:
- `lease_ctx_info` holds parsed SMB2 create lease request data, including lease key, requested state, flags, duration, parent lease key, epoch, version, and directory flag.
- `lease_table` groups leases by client GUID.
- `lease` stores active granted lease state and metadata.
- `oplock_info` binds a lease/oplock to connection, session, work, file, level, state, FID/TID, pending break bit, refcount, break count, wait queues, and list nodes.
- `lease_break_info` and `oplock_break_info` are small work payloads for async break notifications.

Exported behavior:
- Grant and break: `smb_grant_oplock`, `smb_break_all_levII_oplock`, `smb_break_all_oplock`, `close_id_del_oplock`.
- State transitions: `opinfo_write_to_read`, `opinfo_read_handle_to_read`, `opinfo_write_to_none`, `opinfo_read_to_none`, `lease_read_to_write`.
- Lookup/lifetime: `opinfo_get`, `opinfo_put`, `lookup_lease_in_table`, `find_same_lease_key`, `destroy_lease_table`.
- Create-context utilities: lease parsing, lease/oplock mapping, durable response builders, POSIX response builder, and context lookup.
- Durable reconnect validation: `smb2_check_durable_oplock`.

Role in this group:
- `oplock.c` implements the state machine.
- SMB2 create/close/write/ioctl paths include this header to coordinate client-side caching semantics with server-side file operations.
