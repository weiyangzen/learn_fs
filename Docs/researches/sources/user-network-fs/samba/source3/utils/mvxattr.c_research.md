<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mvxattr.c -->
# sources/user-network-fs/samba/source3/utils/mvxattr.c

## Purpose
`mvxattr.c` recursively renames an extended attribute from one name to another on one or more filesystem paths. It is an administrative migration helper for xattr namespace/key changes.

## Important APIs, types, and functions
- Global `state` stores `follow_symlink`, `print`, `force`, `verbose`, `xattr_from`, and `xattr_to`.
- `rename_xattr()` is the `nftw()` callback. It reads the source xattr, writes the destination xattr with create or replace semantics, removes the source xattr, and optionally prints the rename.
- `main()` enforces root, parses `--from`, `--to`, `--follow-symlinks`, `--print`, `--verbose`, and `--force`, validates paths, and invokes `nftw()` for each path.

## Control flow
The program exits unless run as root. After option parsing, each positional path is traversed with `nftw()` using `FTW_PHYS` unless symlink following is requested. The callback ignores symlink entries, skips files without the source xattr, copies the exact xattr value into a variable-length stack buffer, creates the destination xattr, optionally replaces it under `--force`, removes the source xattr, and returns nonzero on error.

## State and persistence behavior
The tool mutates filesystem xattrs in place. A successful operation removes `state.xattr_from` and writes `state.xattr_to` with the same bytes. If destination write succeeds but source removal fails, both xattrs may remain. It does not maintain rollback state.

## Dependencies and integration points
It depends on POSIX/nftw traversal, platform xattr APIs (`getxattr`, `setxattr`, `removexattr`), popt, talloc, and Samba output helpers. It is intended for local filesystem administration, not SMB protocol access.

## Risks and edge cases
- Must run as root, likely because xattrs of interest may be privileged.
- The xattr value is stored in a variable-length stack array sized from `getxattr`; very large xattrs can stress stack limits.
- Symlink handling is partly duplicated: traversal can avoid following symlinks and the callback also ignores `FTW_SL`.
- Return status for multiple paths is overwritten by the last `nftw()` call.
- No rollback exists for partial failures.

## Test signals
Tests can create temporary files with source xattrs, run forced and non-forced destination cases, verify source removal and byte preservation, confirm missing source xattrs are skipped, and validate symlink traversal modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mvxattr.c -->
