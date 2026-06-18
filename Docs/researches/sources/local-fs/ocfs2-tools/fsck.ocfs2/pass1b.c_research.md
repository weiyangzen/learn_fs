# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1b.c

Purpose: implements extra fsck passes 1B through 1D, invoked when pass 1 found clusters claimed by more than one object; it discovers ownership, names affected inodes, and repairs duplicate claims by refcount conversion, cloning, or deletion.

Read coverage: complete file read, 1,615 lines.

Key responsibilities:
- Pass 1B rescans valid inodes and records owners of clusters present in `ost_duplicate_clusters`.
- Tracks duplicate clusters in an rbtree keyed by physical cluster and duplicate inodes in an rbtree keyed by inode block.
- Handles duplicate ownership in normal extent trees, chain allocator group descriptors, discontiguous block groups, inline/external xattrs, xattr trees, and xattr buckets.
- Pass 1C walks root and system directory trees to attach paths to duplicate-owning inodes for user-facing repair prompts.
- Pass 1D reports duplicate clusters and first attempts to turn shared data into proper refcounted extents when refcount-tree support makes that safe.
- If refcount conversion is not possible or declined, repairs duplicate claims by cloning file data to a new inode, swapping extent trees, deleting the temporary clone, or deleting the original inode.
- Prevents deletion of system files and refuses clone/delete repair of chain allocator inodes.

Important entry points:
- `ocfs2_pass1_dups()` orchestrates 1B, 1C, and 1D and frees duplicate tracking structures.
- `o2fsck_pass1b()` performs the duplicate owner rescan.
- `pass1b_process_inode()` routes inode-owned storage through extent, chain, and xattr processors.
- `o2fsck_pass1c()` names duplicate inodes by directory traversal.
- `o2fsck_pass1d()` performs user-driven repair.
- `o2fsck_create_refcount()` creates or attaches refcount trees and marks shared extents refcounted.
- `clone_one_inode()`, `new_clone()`, `copy_clone()`, `swap_clone()`, and `delete_one_inode()` implement clone/delete repair.

Dependencies:
- Uses `ost_duplicate_clusters` from pass 1, libocfs2 extent/xattr/chain iteration, cached inode I/O, file read/write, allocation, truncation, delete, and refcount APIs.
- Uses kernel rbtree/list compatibility headers, directory iteration, inode count maps, and prompt problem codes.

Risk and edge cases:
- These passes are explicitly expensive and avoid relying on the I/O cache as heavily as pass 1.
- Clone repair intentionally does not link the temporary clone into the orphan directory because during the process it may temporarily point at multiply claimed clusters.
- If fsck crashes between clone inode and original inode writes, comments describe the next fsck as able to recover by detecting the remaining duplicate/unreferenced state.
- Refcount conversion is only attempted when all owners are non-system files and either share the same refcount tree or have none.
- Chain allocators with duplicate clusters cannot be cloned or deleted; fsck only warns that the filesystem may need read-only data evacuation.
