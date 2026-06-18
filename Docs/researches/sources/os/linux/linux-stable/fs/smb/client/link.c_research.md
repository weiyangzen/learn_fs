# File Research: sources/os/linux/linux-stable/fs/smb/client/link.c

Read status: complete.

## Purpose

Implements CIFS/SMB hardlink and symlink creation plus Minshall+French symlink parsing, formatting, querying, and creation helpers.

## Main Responsibilities

- Recognize MF symlink placeholder files by size and payload format.
- Parse MF symlink files and expose them as Linux symlinks.
- Create MF symlink placeholder files when that symlink mode is selected.
- Provide SMB1 and SMB2/3 MF symlink query/create operations.
- Implement hardlink creation through legacy Unix extensions or dialect-specific SMB operations.
- Implement symlink creation through legacy Unix symlinks, MF symlinks, SFU emulation, or native/NFS/WSL reparse symlinks.

## Important Functions

- `parse_mf_symlink()`
  - Validates fixed MF symlink file size.
  - Parses `XSym` length, validates target length, recomputes MD5 over the target, compares encoded digest, and optionally returns a copied target string.

- `format_mf_symlink()`
  - Builds the fixed-size MF symlink payload with length header, MD5 digest, target string, newline, and padding.

- `couldbe_mf_symlink()`
  - Fast screen for regular files whose EOF exactly matches MF symlink file size.

- `create_mf_symlink()`
  - Formats an MF symlink buffer and calls `server->ops->create_mf_symlink`.
  - Verifies the server wrote the full fixed-size payload.

- `check_mf_symlink()`
  - Reads and parses a possible MF symlink.
  - On success, rewrites `fattr` as a symlink with `0777`-style permission bits and transfers the target into `cf_symlink_target`.

- `cifs_query_mf_symlink()` / `cifs_create_mf_symlink()`
  - SMB1-specific open/read/write helpers for MF symlink files.

- `smb3_query_mf_symlink()` / `smb3_create_mf_symlink()`
  - SMB2/SMB3 variants using UTF-16 paths, `SMB2_open`, `SMB2_read`, `SMB2_write`, and `SMB2_close`.

- `cifs_hardlink()`
  - Creates hardlinks via legacy Unix extension or `server->ops->create_hardlink`.
  - Drops the target dentry to force fresh lookup.
  - Locally increments source nlink when creation succeeds and clears tmpfile state.

- `cifs_symlink()`
  - Selects symlink strategy from mount/server state.
  - Supports legacy Unix, MF symlink files, SFU node creation, and reparse-point symlinks.
  - Queries and instantiates the new inode after successful non-reparse symlink creation.

## Dependencies

- Uses crypto MD5 helper, CIFS path building, dialect open/read/write/close operations, SMB2 protocol helpers, reparse symlink creation, SFU node creation, and inode metadata refresh helpers from `inode.c`.

## Notable Behaviors

- Invalid MF payloads are treated as “not a symlink” rather than hard errors.
- MF symlink detection is intentionally size-gated before issuing expensive reads.
- SMB2/3 MF creation checks for short writes and maps them to traceable `-EIO`.
- Hardlink creation updates local nlink only for the source inode and still forces future revalidation.
