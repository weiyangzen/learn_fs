# sources/user-network-fs/samba/source3/modules/vfs_cap.c

## Purpose
`vfs_cap.c` implements Samba's legacy CAP filename encoding module. It maps bytes with the high bit set to a `:xx` hexadecimal representation before passing paths to the underlying filesystem, and decodes directory entries back for SMB clients. This supports environments that need CAP-style storage names for non-ASCII byte values.

## Important APIs, types, and functions
- `capencode()` converts every byte `>= 0x80` to `:<lower-hex><lower-hex>`.
- `capdecode()` converts `:xx` sequences back to bytes using `hex_byte()`.
- Path wrappers such as `cap_mkdirat()`, `cap_openat()`, `cap_fstatat()`, `cap_stat()`, `cap_lstat()`, `cap_unlinkat()`, `cap_lchown()`, `cap_chdir()`, `cap_mknodat()`, and `cap_realpath()` encode names before delegating.
- Link and symlink wrappers encode both source/target and destination components as needed.
- `cap_readdir()` delegates `READDIR`, decodes `d_name`, and returns a talloc-backed replacement `struct dirent`.
- `cap_fgetxattr()`, `cap_fremovexattr()`, and `cap_fsetxattr()` encode xattr names before delegation.
- `cap_create_dfs_pathat()` and `cap_read_dfs_pathat()` encode DFS reparse/symlink paths and preserve returned stat information.
- `vfs_cap_fns` registers the wrappers and explicitly marks async getxattr-at as not implemented.

## Control flow
Most entry points allocate an encoded name under `talloc_tos()`, construct or copy an `smb_filename`, replace `base_name`, call the next VFS operation, and restore/preserve `errno` where the code expects cleanup to run after failure. Operations that receive directory-relative names sometimes build full paths first and then delegate relative to `conn->cwd_fsp`, preserving the historical CAP behavior of encoding the complete backing-store path. Directory reads run in the reverse direction: they fetch the next entry, decode the exposed name, copy the `dirent`, and substitute the decoded `d_name`.

## State and persistence behavior
The persistent state is encoded filenames on the backing filesystem. The module has no durable configuration or cache. Temporary encoded/decoded strings and synthetic `smb_filename` objects are talloc-scoped. Because filenames are stored encoded, disabling the module changes what names clients see and which paths operations resolve.

## Dependencies and integration points
The module depends on Samba VFS path helpers, `synthetic_smb_fname()`, `synthetic_pathref()`, `full_path_from_dirfsp_atname()`, fsp structures, and hexadecimal utility functions. It is registered in `wscript_build` as `vfs_cap` and loaded with `vfs objects = cap`.

## Risks and edge cases
- `capdecode()` treats any colon as a hex tag and advances three bytes without validating that two hex digits follow, so literal colon names or malformed CAP names can decode unexpectedly.
- CAP encoding is byte-oriented, not Unicode-aware, and can conflict with modern filename normalization expectations.
- Some functions preserve `errno` carefully, while others return after talloc cleanup without saving it consistently.
- Several operations use full-path encoding and `cwd_fsp`, which can be sensitive to directory handle semantics.
- `cap_linkat()` has duplicated `TALLOC_FREE(old_full_fname)` calls, harmless under talloc but a maintenance smell.

## Test signals
No targeted tests were found in the inspected tree. Useful tests should create filenames containing high-bit bytes, verify backing-store `:xx` names, list through Samba and confirm decoded names, exercise rename/link/symlink/DFS/xattr paths, and include malformed colon sequences. Build registration in `wscript_build` is the static integration signal.
