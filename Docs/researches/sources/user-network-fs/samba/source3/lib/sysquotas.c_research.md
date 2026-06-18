## sources/user-network-fs/samba/source3/lib/sysquotas.c

Purpose: high-level quota dispatcher. It maps a Samba path/device to a mount path, block device, and filesystem type, optionally delegates to configured quota commands, and otherwise calls filesystem-specific quota backends or default VFS quota wrappers.

Important helpers are `sys_dev_to_bdev`, multiple `sys_path_to_bdev` variants, `command_get_quota`, `command_set_quota`, and exported `sys_get_quota`/`sys_set_quota`. The `sys_quota_backends` table registers JFS2, XFS/GFS/GFS2, and NFS backends when compiled.

Control flow: `sys_get_quota` and `sys_set_quota` first try `lp_get_quota_command`/`lp_set_quota_command` via `file_lines_ploadv`, using argv-style execution and parsing/formatting `SMB_DISK_QUOTA` fields. If no command is configured (`ENOSYS`), they resolve mount metadata. Linux-like systems prefer `/proc/self/mountinfo`; fallback walks `realpath` components to the mount root and scans `setmntent`. Then they match `fs` against specialized backends, else call `sys_get_vfs_quota`/`sys_set_vfs_quota`.

State and persistence: no durable state except external quota changes. `sys_dev_to_bdev` caches inability to open `/proc/self/mountinfo` in a static boolean. Dependencies include loadparm substitution, mount tables, stat wrappers, quota backend symbols, talloc, command execution helpers, and `SMB_DISK_QUOTA`.

Risks: command output parsing expects seven fields even though it initializes and scans an eighth `bsize` field, so bsize override handling is suspect. Mountinfo parsing is Linux-specific and assumes field positions. Fallback realpath/stat mount discovery can race with remounts. Tests should cover command delegation, malformed command output, mountinfo parsing, filesystem backend selection, NFS unsupported set, and cleanup of talloc-owned mount strings.
