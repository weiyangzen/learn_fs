# File Research: sources/os/linux/linux/fs/smb/server/mgmt/share_config.c

This file manages cached share configuration fetched from the userspace IPC daemon.

Main behavior:
- Maintains `shares_table`, a hash table keyed by casefolded share name under `shares_table_lock`.
- `share_config_request()` asks userspace for share configuration, validates the returned name against the requested name, allocates `struct ksmbd_share_config`, copies flags/masks/forced IDs, parses veto-list payloads, normalizes the path, and resolves it with `kern_path()` under overridden filesystem IDs.
- Pipe shares skip filesystem path setup.
- Existing cache entries win if another thread inserted the share while IPC was in progress.
- Reference counting is atomic; final put removes from the hash and frees veto patterns, path, name, and vfs path.
- `ksmbd_share_veto_filename()` matches filenames against configured veto wildcard patterns.

This module bridges userspace share configuration into kernel path and permission metadata used by tree connects and VFS operations.
