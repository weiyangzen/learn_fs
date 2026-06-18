# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_mangle_name.c

This file implements DOS/8.3 filename validation, short-name mangling, mangled-name detection, and unmangling by directory scan.

Key responsibilities:
- Detects invalid SMB/DOS filenames and reserved DOS device names.
- Determines whether a filename needs 8.3 mangling.
- Generates deterministic mangled names using a base-36 encoding of inode/FID.
- Detects whether an incoming name looks like a mangled 8.3 name.
- Resolves a mangled name back to the real directory entry by scanning the directory and remangling each candidate.

Important functions:
- `smb_is_invalid_filename` rejects control/special invalid characters except spaces and checks reserved DOS names.
- `smb_is_reserved_dos_name` recognizes `CON`, `PRN`, `AUX`, `NUL`, `CLOCK$`, `COM1`-`COM9`, and `LPT1`-`LPT9`, including extension forms like `NUL.txt`.
- `smb_needs_mangled` applies 8.3 naming rules, dot counts, invalid/special character checks, and leading-dot handling.
- `smb_generate_mangle` produces a `~` plus base-36 suffix.
- `smb_maybe_mangled` checks validity, tilde placement, dot count, and 8.3 length.
- `smb_mangle` constructs uppercase DOS-compatible base and extension portions.
- `smb_unmangle` scans directory entries, validates UTF-8, remangles each name with its inode, and compares case-insensitively.

Filesystem relevance:
- `smb_unmangle` uses `smb_vop_readdir` against the directory vnode.
- It uses directory entry inode numbers as the unique input to `smb_mangle`.
- Returned names are real filesystem names copied into caller-provided buffers.

Edge cases and protections:
- `.` and `..` are never mangled.
- Leading dots force mangling except for `.` and `..`.
- Invalid DOS characters are dropped during mangling; selected special characters are converted to `_`.
- Non-UTF-8 directory names are skipped during unmangling.
- Partial directory records are defensively skipped by restarting at the current offset.
- `flags` in `smb_unmangle` is retained only for caller compatibility and is unused.
