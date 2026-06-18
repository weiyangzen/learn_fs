# File Research: sources/teaching/minix/minix/fs/isofs/susp_rock_ridge.c

This file implements Rock Ridge Interchange Protocol parsing for isofs.

Key functions:
- `parse_susp_rock_ridge_plcl(dir, block)`: handles relocated/reparented directories by loading or reusing the inode at a target block.
- `parse_susp_rock_ridge_sl(dir, buffer, length)`: parses symbolic link components.
- `parse_susp_rock_ridge(dir, buffer)`: dispatches individual Rock Ridge entries.

Supported Rock Ridge entries:
- `PX`: POSIX mode, UID, GID.
- `PN`: device major/minor.
- `SL`: symbolic link target.
- `NM`: alternate POSIX name.
- `PL`/`CL`: parent/child link relocation.
- `RE`, `SF`: ignored.
- `TF`: POSIX timestamps in 7-byte ISO format; 17-byte format noted unsupported.

Important behavior:
- Symbolic link parsing handles normal components plus `.`, `..`, and root.
- Name and symlink buffers are bounded by `ISO9660_RRIP_MAX_FILE_ID_LEN`.
- Reparenting may reuse an already cached inode or read a target directory record to create one.

Notable risks:
- Several fields are read with direct casts from unaligned buffer offsets.
- Timestamp parsing comment notes 17-byte TF format is unsupported.
- PN parsing has a Minix-specific workaround guarded by disabled standard interpretation.
