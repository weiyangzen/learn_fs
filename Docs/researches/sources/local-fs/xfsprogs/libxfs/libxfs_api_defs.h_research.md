# File Research: sources/local-fs/xfsprogs/libxfs/libxfs_api_defs.h

Namespace mapping header for exposing kernel-derived XFS functions through libxfs names.

Key responsibilities:
- Maps many `xfs_*` symbols to `libxfs_*` symbols with preprocessor defines.
- Covers attr, bmap, btree, buffer, directory, quota, inode, metadir, parent pointer, perag, allocation, rmap, refcount, realtime, superblock, symlink, transaction, verifier, and geometry APIs.
- Defines exported attr namespace aliases.

Important behavior:
- Kept separate so internal and external libxfs headers can share mappings without circular dependencies.
- Comment requests the list remain alphabetized, though realtime sections include repeated mappings.

Dependencies:
- Included wherever kernel-style source wants to call libxfs-renamed implementations.

Notable risks:
- Macro aliasing is broad and can obscure which implementation is actually linked.
- Duplicate realtime mappings and ordering drift can make maintenance error-prone.
