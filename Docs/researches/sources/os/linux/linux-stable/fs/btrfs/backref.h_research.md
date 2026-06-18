# File Research: sources/os/linux/linux-stable/fs/btrfs/backref.h

## Summary
Declares Btrfs backreference walking APIs, sharedness-check contexts, inode/path containers, metadata backref iterators, and relocation backref-cache structures.

## Main Contents
- `iterate_extent_inodes_t` callback protocol and stop code.
- `struct btrfs_backref_walk_ctx` for generic extent backref walks.
- `struct inode_fs_paths` and data-container helpers.
- `struct btrfs_backref_share_check_ctx` and caches.
- Public APIs for logical extent lookup, inode iteration, path resolution, leaf/root discovery, extref lookup, and sharedness checks.
- `struct prelim_ref` and `struct btrfs_backref_iter`.
- Backref cache node/edge/cache structures and cache management APIs.

## Important Behavior
The walk context distinguishes data extent position filtering, whole-extent matching, optional inode-list suppression, transaction versus commit-root walking, and callbacks for leaf-root caching, early indirect data iteration, extent-item checking, and data-ref skipping.

The backref cache is explicitly a bidirectional map of tree blocks and parents. Nodes track bytenr, new bytenr, owner, root, extent buffer, level, lock/processed/checked/pending/detached state, and relocation-root status. Edges link lower and upper nodes through separate list heads.

## Risks
The header exposes several multi-step protocols: allocate/init/release contexts, prepare iterator/start/next, add tree node then finish upper links, and error cleanup. Callers must preserve context fields and ownership rules expected by `backref.c`.
