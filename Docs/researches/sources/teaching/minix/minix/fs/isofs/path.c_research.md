# File Research: sources/teaching/minix/minix/fs/isofs/path.c

This file implements isofs component lookup.

Key functions:
- Internal `search_dir(ldir_ptr, string, numb)`: validates directory, loads cached directory contents, handles `"."`, and linearly searches names.
- `fs_lookup(dir_nr, name, node, is_mountpt)`: finds parent inode, resolves child inode number, opens child inode, and returns fsdriver node metadata.

Behavior:
- Read-only lookup over cached directory arrays.
- Uses Rock Ridge names when directory loading chose them.
- Returns `ENOTDIR`, `ENOENT`, `EINVAL`, or `EIO` depending on failure stage.

Notable detail:
- Lookup opens the resulting inode but does not release the parent because `get_inode()` does not increment the parent reference.
