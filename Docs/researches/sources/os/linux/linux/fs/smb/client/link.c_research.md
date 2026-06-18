# File Research: sources/os/linux/linux/fs/smb/client/link.c

## Purpose
Implements SMB client hardlink and symlink creation plus Minshall+French symlink detection, parsing, creation, and protocol-specific read/write helpers.

## Main Interfaces
- MF symlink helpers: `couldbe_mf_symlink()`, `check_mf_symlink()`, `cifs_query_mf_symlink()`, `cifs_create_mf_symlink()`, `smb3_query_mf_symlink()`, `smb3_create_mf_symlink()`.
- VFS link operations: `cifs_hardlink()` and `cifs_symlink()`.

## Control Flow
MF symlinks are represented as fixed-size regular files containing an `XSym` header, a length, an MD5 of the target, and the target string padded to `CIFS_MF_SYMLINK_FILE_SIZE`. Detection first checks regular-file type and size, then reads and validates the header/hash before changing the fattr to a symlink with the decoded target.

Hardlink creation builds source and destination paths, uses legacy Unix extensions when available, otherwise calls the dialect `create_hardlink()` operation. Symlink creation chooses the configured symlink strategy: Unix extension symlink, MF symlink, SFU node, or native/NFS/WSL reparse symlink when reparse support is available.

## State And Synchronization
Hardlink success updates the source inode link count locally and clears `CIFS_INO_TMPFILE`. Source inode attribute cache time is invalidated so later stat can reconcile with server state.

## Integration Points
Calls SMB1 open/read/write/close helpers for legacy MF symlink access and SMB2 open/read/write/close helpers for SMB2/3. Uses inode metadata lookup from `inode.c` after successful symlink creation and reparse symlink creation from `reparse.c`.

## Notable Behaviors
- MF symlink writes require the full fixed-size payload or return an SMB EIO trace error.
- MF symlink parsing treats malformed fixed-size files as ordinary regular files.
- Native reparse symlink creation exits early because it handles dentry instantiation in the reparse helper path.
- Hardlink target dentry is dropped to force a fresh lookup.

## Risks And Review Focus
- MF symlink validation relies on fixed offsets and MD5 string formatting.
- Symlink behavior varies substantially by mount option and server capability.
- Hardlink metadata is partly updated locally under oplock/cache assumptions.
