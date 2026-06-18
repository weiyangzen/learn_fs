# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/paths.c

This file implements libpuffs path construction and path comparison helpers used when a mount is created with `PUFFS_FLAG_BUILDPATH`. `puffs_path_pcnbuild` builds the full path for a component name relative to a parent puffs node, optionally applying a path transform and name modifier, then calls the configured `pu_pathbuild` routine and computes a hash if path hashing is enabled.

`puffs_path_prefixadj` is intended for nodewalk use after rename. It checks whether each node path has the old path as a full prefix, constructs a replacement path with the new prefix plus the suffix after the old prefix, updates the path hash, frees the old path object, and continues walking. If path rebuilding fails, the function aborts because partially rewritten path state would be inconsistent.

`puffs_path_walkcmp` performs exact path matching for node walks. It first checks length, then optionally rejects by stored hash, then calls the configured path comparator to handle exact comparison and collisions.

`puffs_path_buildhash` selects `hash32_strn` when using the standard string path builder and `hash32_buf` otherwise. The standard path functions treat paths as slash-separated strings: `puffs_stdpath_cmppath` compares exact paths or full-prefix matches, `puffs_stdpath_buildpath` joins parent and component paths, strips extra slashes, handles `..`, preserves root semantics, and allocates a new path string, and `puffs_stdpath_freepath` frees it.
