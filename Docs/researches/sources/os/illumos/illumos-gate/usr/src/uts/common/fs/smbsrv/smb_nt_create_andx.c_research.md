# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_create_andx.c

## Summary
Implements SMB1 `NT_CREATE_ANDX`, the main SMB1 open/create command for files, directories, pipes, and printers. It decodes protocol parameters into `open_param`, delegates the real work to `smb_common_open()`, optionally acquires SMB1 oplocks, and encodes normal or extended create responses.

## Main Responsibilities
- Decodes name, desired access, share access, allocation size, attributes, disposition, create options, impersonation, and security flags.
- Converts NT create flags into requested oplock level.
- Validates create options, disposition, delete-on-close access, and file-id opens.
- Handles root-directory-relative opens through an existing directory FID.
- Applies backup-intent credentials.
- Sets delete-on-close on successful disk/printer opens.
- Encodes standard or Windows-compatible extended responses.

## Key APIs
- `smb_pre_nt_create_andx()`.
- `smb_post_nt_create_andx()`.
- `smb_com_nt_create_andx()`.

## Important Behavior
`FILE_OPEN_BY_FILE_ID` is rejected as unsupported. `FILE_DELETE_ON_CLOSE` requires `DELETE` access. `FILE_FLAG_WRITE_THROUGH`, `FILE_FLAG_DELETE_ON_CLOSE`, and `FILE_FLAG_BACKUP_SEMANTICS` are translated into create options before the common open path.

If `RootDirectoryFid` is nonzero, the handler looks up that ofile and uses its node as the path root; `smb_post_nt_create_andx()` releases that directory ofile.

Extended responses deliberately encode 50 real words while reporting a fake word count of 42 to match Windows SMB1 behavior. The extended response includes `MaxAccess`, while the file-id field is left zero for compatibility.

## Dependencies
Depends on `smb_common_open()`, SMB1 oplock acquisition, ofile lookup/close, `smb_fsop_eaccess()`, node type checks, and SMB result mbuf encoding.

## Risks
After `smb_common_open()` succeeds, every later encode or resource-type failure must close the newly allocated ofile. The handler does this via `errout`; future edits need to preserve that invariant.

The extended-response path intentionally violates normal SMB word-count encoding rules, so generic response helpers cannot be used there.
