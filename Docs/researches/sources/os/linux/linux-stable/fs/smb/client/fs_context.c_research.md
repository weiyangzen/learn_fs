# File Research: sources/os/linux/linux-stable/fs/smb/client/fs_context.c

## Summary
Implements CIFS/SMB3 mount-context parsing, validation, initialization, cleanup, mount tree creation, and remount/reconfigure handling for the Linux fs_context mount API. It owns the option table for `cifs`/`smb3`, SMB dialect selection, security/cache/reparse/symlink flavor parsing, UNC parsing, mount defaults, mount flag synthesis, password synchronization, and multichannel remount updates.

## Main Responsibilities
- Define `smb3_fs_parameters[]`, the full mount-option specification consumed by `fs_parse()`.
- Parse SMB dialects, security flavors, cache modes, upcall target, reparse policy, and symlink policy.
- Parse and normalize UNC source paths into `server_hostname`, `UNC`, `prepath`, and `source`.
- Parse legacy comma-separated monolithic mount option strings for old mount callers.
- Validate required mount state before connecting, including dialect/RDMA compatibility, UNC shape, destination address, and uid/gid override rules.
- Create the root dentry via `cifs_smb3_do_mount()` under the global CIFS mount mutex.
- Duplicate and free `struct smb3_fs_context` contents safely, including sensitive password fields.
- Verify whether remount changes are compatible with the existing session.
- Reconfigure active mounts, including password replacement and multichannel/max-channel changes.
- Translate context booleans into atomic CIFS superblock mount flags.

## Key Interfaces
- Mount API operations are collected in `smb3_fs_context_ops`: free, parse_param, parse_monolithic, get_tree, and reconfigure.
- `smb3_init_fs_context()` allocates a context and installs defaults and fs_context operations.
- `smb3_fs_context_parse_param()` handles every parsed mount parameter and updates `struct smb3_fs_context`.
- `smb3_fs_context_validate()` checks the fully parsed context before mounting.
- `smb3_get_tree()` validates and serializes mount creation with `cifs_mount_lock()`.
- `smb3_reconfigure()` applies compatible remount changes and coordinates session password and multichannel updates.
- `smb3_fs_context_dup()`, `smb3_cleanup_fs_context_contents()`, and `smb3_cleanup_fs_context()` manage context ownership.
- `smb3_update_mnt_flags()` converts context settings into `CIFS_MOUNT_*` flags.
- `smb3_parse_devname()`, `cifs_sanitize_prepath()`, and `smb3_fs_context_fullpath()` implement source path parsing and normalization.

## Control Flow And Behavior
The parameter table accepts flag, negated-flag, uid/gid, integer, u64, and string options. It aliases common mount helper spellings such as `username`, `password`, `vers`, `cache`, `addr`, `domain`, and older ignored options such as `credentials`, `unc`, and `prefixpath`.

`sec=` resets previous security choices so the last security option wins. Kerberos and NTLMSSP integrity variants enable signing. `krb5p` is rejected in favor of `krb5,seal`. `sec=none` enables null authentication and clears the username.

Dialect parsing maps `vers=` to protocol operation/value tables. SMB1 and SMB2.0 are accepted only when insecure legacy dialects are compiled and not disabled, and the `smb3` filesystem name rejects SMB1/SMB2.0 dialect requests. The default is SMB2.1-or-later through SMB3 default values.

UNC parsing requires a leading `//` or `\\`, extracts host and share, converts the UNC to backslash separators, sanitizes duplicated prefix-path delimiters, and builds a slash-delimited `source` string for VFS-visible mount source state. If `ip=` is absent, validation attempts to derive the destination address from the UNC host.

The monolithic parser first lets LSM code consume security options, then splits comma-separated options while preserving doubled delimiters inside values, and feeds each key/value into `vfs_parse_fs_string()`. After parsing, `smb3_handle_conflicting_options()` reconciles `multichannel` and `max_channels`.

Parameter parsing enforces value bounds for block size, readahead size, attribute-cache timeouts, deferred-close timeout, echo interval, max credits, max cached directories, channel count, handle timeout, username/domain/iocharset lengths, and symlink root absoluteness. Unsupported features fail early when their kernel config is absent, such as fscache, compression, witness, or CIFS rootfs support.

Remount validation rejects changes to identity and protocol-defining fields such as posixpaths, security type, multiuser mode, UNC, username, domain, workstation, nodename, iocharset, Unicode mode, and NetBIOS session initialization. Password changes are allowed only when the session needs reconnect and not for Kerberos.

`sm b3_reconfigure()` duplicates the old context for rollback, steals stable strings from the old superblock context into the new context, preserves previous rsize/wsize when absent, synchronizes session passwords under `session_mutex`, updates `ses->chan_max` and invokes channel scaling when multichannel settings changed, commits the new context atomically, refreshes mount flags, and optionally refreshes DFS remount state.

## Defaults And Mount Flag Mapping
Initialization defaults to strict cache semantics, server inode numbers, POSIX paths, SFM character remapping, owner-write-only file/dir modes, current uid/gid credentials, SMB3 default dialect values, one channel, one-second deferred close timeout, default echo interval, default attribute cache timeouts, default max cached directory handles, and Unicode autodetection.

`smb3_update_mnt_flags()` maps context fields into runtime superblock flags for DFS, permission checks, setuid behavior, uid-from-ACL, server inode numbers, filename remapping, xattrs, SFU emulation, byte-range locking, handle caching, strict sync, mandatory locking, read/write pid forwarding, mode-from-SID, CIFS ACLs, backup uid/gid, uid/gid overrides, dynperm, fscache, multiuser, strict/direct I/O, and mfsymlinks. It clears forced shutdown during flag refresh.

## State And Synchronization
The global `cifs_mount_mutex` serializes mount creation. Remount coordinates with `ses->session_mutex`, `ses->chan_lock`, and `ses->ses_lock` when updating credentials and channel counts. Context string ownership is explicit: some fields are duplicated for rollback, some are stolen from the existing superblock context, and password fields are freed with sensitive cleanup.

## Risks
Most risk is in option interaction and ownership. Empty string parameters bypass normal `fs_parse()` handling for username/password fields. Remount must either commit all context/session changes or restore the previous context without leaking or losing sensitive strings. Multichannel updates must avoid racing concurrent scaling. Source parsing and delimiter normalization affect DFS, reconnect, and path construction elsewhere in the client.
