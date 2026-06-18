# File Research: sources/os/linux/linux-stable/fs/smb/server/smb_common.c

## Summary
Implements shared ksmbd SMB protocol helpers: dialect selection, SMB1 negotiate fallback/upgrade handling, request validation, 8.3 short-name generation, directory dot/dotdot population, share-mode conflict checks, temporary fsuid/fsgid credential overrides, and generic access-mask expansion.

## Main Responsibilities
- Maintain SMB dialect tables for SMB1 negotiate names and SMB2/SMB3 dialect IDs.
- Select min/max protocol versions and map protocol indexes to user-visible strings.
- Validate incoming SMB1/SMB2/SMB3 transform request framing before protocol dispatch.
- Negotiate dialects from SMB1 dialect-name arrays or SMB2 dialect-id arrays, honoring `server_conf.min_protocol` and `server_conf.max_protocol`.
- Provide minimal SMB1 negotiate response plumbing, including upgrading SMB1 negotiate requests to SMB2 when the selected dialect is SMB2+.
- Populate `.` and `..` directory entries through caller-supplied directory-info encoders.
- Generate mangled 8.3 short names and convert them to UTF-16.
- Enforce Windows share-mode compatibility among existing and new opens on the same inode/stream.
- Override current credentials to the authenticated user or forced share uid/gid for VFS calls, then restore them.
- Expand generic SMB desired-access bits into concrete file rights.

## Key Interfaces
- Protocol selection: `ksmbd_min_protocol()`, `ksmbd_max_protocol()`, `ksmbd_get_protocol_string()`, `ksmbd_lookup_protocol_idx()`, `ksmbd_lookup_dialect_by_id()`.
- Request setup: `ksmbd_verify_smb_message()`, `ksmbd_smb_request()`, `ksmbd_init_smb_server()`, `ksmbd_smb_negotiate_common()`.
- Directory/open helpers: `ksmbd_populate_dot_dotdot_entries()`, `ksmbd_extract_shortname()`, `ksmbd_smb_check_shared_mode()`.
- Credentials/access: `__ksmbd_override_fsids()`, `ksmbd_override_fsids()`, `ksmbd_revert_fsids()`, `smb_map_generic_desired_access()`.

## Important Behavior
SMB1 support here is negotiate-only. If an SMB1 negotiate packet selects an SMB2 dialect, the connection is initialized as SMB3.1.1-capable and an SMB2 negotiate response is prepared. Other SMB1 commands are rejected.

Share-mode checking walks the inode’s open-file list under `m_lock` and compares requested desired access against previously granted share access and desired access. It special-cases named streams, attribute-only opens, and delete/read/write conflicts.

Credential override builds kernel credentials from ksmbd user config, applies forced share ids, fills supplementary groups, drops fs capabilities for non-root fsuid, and stores the previous cred in `work->saved_cred`.

## Cross-File Interactions
Used by connection dispatch, SMB2 negotiate code, directory enumeration, open/create handling, VFS operations, user/session/share config, and access-control conversion. It depends on `smb2pdu.c` for SMB2 negotiate handling and on `vfs.c`/`vfs_cache.c` types for directory and open-file state.

## Risks
Dialect negotiation and request validation are externally controlled input paths. Share-mode checks are concurrency-sensitive because they depend on open-file list lifetime and stream identity. Credential override/revert must stay balanced around every VFS operation to avoid running later filesystem work under the wrong identity.
