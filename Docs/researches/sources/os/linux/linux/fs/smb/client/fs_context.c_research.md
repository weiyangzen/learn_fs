# File Research: sources/os/linux/linux/fs/smb/client/fs_context.c

## Role

Implements the SMB3/CIFS Linux `fs_context` mount API: mount option specification, option parsing, UNC/source path parsing, dialect/security/cache/symlink/reparse parsing, mount validation, superblock creation, remount/reconfigure handling, context duplication/cleanup, and conversion from parsed context fields to CIFS mount flags.

## Mount Parameter Surface

- `smb3_fs_parameters[]` declares supported mount options for the new mount API.
- Flag options cover permissions, lease/cache behavior, DFS, POSIX/UNIX extensions, byte-range locking, ACLs, signing/sealing, FS-Cache, multiuser, sharesock, persistent/resilient handles, RDMA, multichannel, compression, witness, native sockets, Unicode, NetBIOS session init, and rootfs.
- Numeric options include UID/GID, modes, port, I/O sizes, attribute cache timeouts, deferred close timeout, echo interval, max credits, cached directories, snapshot time, handle timeout, and max channels.
- String options include source, user/passwords, IP/srcaddr, domain, charset, NetBIOS names, dialect/security/cache selections, reparse/symlink policy, upcall target, and symlink root.
- Compatibility/old mount-helper options such as `cred`, `credentials`, `unc`, and `prefixpath` are ignored.

## Parsers

- `cifs_parse_security_flavors()` maps `sec=` strings to Kerberos, RawNTLMSSP, NTLMv2, or null auth; integrity variants set signing, and unsupported `krb5p` is rejected with guidance to use sealing.
- `cifs_parse_smb_version()` maps `vers=` to protocol operation/value tables and rejects insecure legacy dialects when unavailable or when mounting via the `smb3` filesystem type.
- `cifs_parse_cache_flavor()` maps `cache=` to direct I/O, strict cache, loose cache, read-only cache, or single-client read/write cache.
- `parse_reparse_flavor()` and `parse_symlink_flavor()` configure how Windows reparse points and SMB symlinks are interpreted.
- `cifs_parse_upcall_target()` selects mount-namespace vs application-namespace upcalls.
- `smb3_fs_context_parse_param()` is the main option dispatcher. It handles empty string user/password values, validates bounds, aligns rsize/wsize/bsize, parses addresses, normalizes conflicting options, enforces kernel config requirements, owns copied strings, and rejects invalid combinations such as `multiuser` with `upcalltarget=mount`.

## Path And Source Handling

- `cifs_sanitize_prepath()` removes duplicate leading/interior/trailing path delimiters and returns `NULL` for empty prefix paths.
- `smb3_parse_devname()` validates UNC syntax, extracts server hostname, UNC share path, and optional prepath, and converts UNC delimiters to backslashes.
- `smb3_fs_context_fullpath()` rebuilds the full source string from UNC plus prepath with a caller-selected delimiter.
- `smb3_fs_context_parse_monolithic()` parses legacy comma-separated mount option blobs, strips LSM options first, and tolerates doubled delimiters inside values.

## Validation And Mount Creation

- `smb3_fs_context_validate()` rejects RDMA on dialects older than SMB3, rejects multiuser without key support, warns when no dialect is specified, validates UNC/share presence, derives destination IP from UNC if `ip=` was not supplied, sets the port, and normalizes implicit/invalid `forceuid` and `forcegid`.
- `smb3_handle_conflicting_options()` reconciles `multichannel` and `max_channels`, defaulting to one channel unless multichannel is requested or implied by `max_channels > 1`.
- `smb3_get_tree()` validates the context, serializes mount with `cifs_mount_mutex`, and calls `cifs_smb3_do_mount()`.

## Reconfigure/Remount

- `smb3_verify_reconfigure_ctx()` rejects remount changes that would alter immutable session identity or protocol properties: POSIX paths, security type, multiuser, UNC, username, domain, workstation, nodename, charset, Unicode mode, and NetBIOS session init. Password changes are allowed only for expired-password reconnect and not for Kerberos.
- `smb3_reconfigure()` duplicates old context for rollback, preserves immutable strings from the active superblock context, handles password/password2 updates, carries forward previous rsize/wsize if omitted, duplicates the new context, synchronizes session passwords, optionally scales multichannel state, commits the new context atomically, updates mount flags, and triggers DFS remount handling when configured.
- `smb3_sync_session_ctx_passwords()` keeps the superblock context in sync with session passwords that may have been swapped during reconnect.
- `smb3_sync_ses_chan_max()` updates session channel maximum under `chan_lock`.

## Defaults, Cleanup, And Mount Flags

- `smb3_init_fs_context()` allocates `struct smb3_fs_context` and initializes defaults: workstation/NetBIOS names from UTS nodename, current UID/GID, 1 MiB block size, SFM remapping, owner-write modes, POSIX paths, server inode numbers, strict caching, default attribute cache and deferred-close timeouts, cached directory limit, SMB2.1+ default dialect values, echo interval, single-channel operation, default reparse/symlink policy, and Unicode autodetect.
- `smb3_cleanup_fs_context_contents()` frees all owned strings, using sensitive freeing for passwords, and is kept in sync with context duplication.
- `smb3_update_mnt_flags()` maps parsed context booleans into atomic CIFS mount flags, including DFS, permission checks, UID/GID override, char remapping, xattrs, SFU emulation, byte-range locking, handle cache, sync behavior, ACLs, backup UID/GID, dynperm, FS-Cache, multiuser, strict/direct I/O, and mfsymlinks.

## Dependencies

Uses Linux `fs_context`/`fs_parser`, security LSM mount option parsing, CIFS protocol operation/value tables, address parsing helpers, DFS optional support, session/channel locking, and mount/superblock CIFS state.

## Research Notes

This file is the policy boundary between user mount options and runtime SMB client behavior. The highest-risk paths are string ownership during parsing/reconfigure, remount rollback, credential updates during expired-password reconnect, and multichannel scaling coordination with reconnect/channel management.
