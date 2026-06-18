# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_lookup.c

Source read: complete file, 213 lines.

Purpose: HPFS directory lookup and placeholder write-side directory entry operations.

Key interfaces:
- `hpfs_genlookupbyname()` traverses the HPFS directory B+tree from the first directory block in the parent fnode allocation data, compares Unix-encoded input names against on-disk names with codepage-aware case folding, follows `DE_DOWN` child pointers, and returns the buffer plus matching `hpfsdirent`.
- `hpfs_makefnode()` is a create helper stub that returns `EOPNOTSUPP`.
- `hpfs_removedirent()` contains disabled deletion logic under `#if 0` and currently returns `EOPNOTSUPP`.
- `hpfs_removefnode()` is a remove helper stub that returns `EOPNOTSUPP`.

Integration:
- `hpfs_lookup()` in `hpfs_vnops.c` uses `hpfs_genlookupbyname()` for VOP lookup.
- Parent metadata update in `hpfs_updateparent()` uses `hpfs_genlookupbyname()` to find the cached child dirent.

Risks and review notes:
- Directory creation and removal are not implemented despite VOP stubs routing to these helpers.
- Lookup trusts directory record lengths enough to step through blocks; malformed media can cause invalid pointer traversal if earlier structure checks are insufficient.
