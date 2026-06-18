# File Research: sources/os/linux/linux-stable/fs/smb/server/smb_common.h

## Summary
Defines common ksmbd SMB protocol constants, shared wire structures, protocol operation tables, and helper prototypes used across the SMB server implementation.

## Main Responsibilities
- Define ksmbd protocol indexes for SMB1, SMB2.0/2.1, SMB3.0/3.02/3.1.1, and invalid protocol values.
- Define generic access-right expansions and file-open result constants.
- Provide SMB1 negotiate response and selected SMB query-directory structures.
- Declare `struct smb_version_ops` and `struct smb_version_cmds`, the per-dialect dispatch contract used by connections.
- Export common negotiation, request-validation, directory, share-mode, credential, copychunk-limit, and access-mask helpers.
- Provide `smb_get_msg()` to skip the four-byte RFC1002 length prefix.

## Key Interfaces
Important declarations include `ksmbd_verify_smb_message()`, `ksmbd_smb_request()`, `ksmbd_init_smb_server()`, `ksmbd_smb_negotiate_common()`, `ksmbd_smb_check_shared_mode()`, `ksmbd_override_fsids()`, `ksmbd_revert_fsids()`, and `smb_map_generic_desired_access()`.

## Cross-File Interactions
Included by most server protocol, transport, VFS, ACL, and connection files. The operation-table definitions are installed by SMB1 compatibility code and SMB2 dialect setup code.

## Risks
This header is a broad internal ABI. Changing access constants, operation-table callbacks, or wire structures affects protocol dispatch, negotiate behavior, and open/access checks across ksmbd.
