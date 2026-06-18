# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass3.c

This file implements `fsck.gfs2` pass 3, the directory connectivity pass. It verifies that every directory discovered earlier is connected to the root/master tree, reconciles disagreements between a directory’s `..` entry and the parent observed during tree walking, and offers to reconnect or clear orphaned directories.

The main entry point is `pass3(struct fsck_cx *cx)`. It marks the root and master directory as connected, then iterates `cx->dirtree`. For each unchecked directory, it repeatedly calls `mark_and_return_parent()` to climb toward an already checked parent. If no valid parent chain can be found, it handles the directory as unlinked.

`mark_and_return_parent()` compares `di->dotdot_parent` and `di->treewalk_parent`. If they match and point at a dinode, the directory is considered connected through that parent. If they disagree, it checks bitmap state and `dirtree` membership for both candidates. It can repair `..` by calling `attach_dotdot_to()`, remove bad treewalk dentries via `remove_dentry_from_dir()`, or signal that the directory should be treated as orphaned.

Orphan handling loads the inode, checks bitmap type, clears invalid or zero-size orphaned directories when permitted, or calls `add_inode_to_lf()` to relink valid unlinked directories into `lost+found`.

Dependencies include `libgfs2`, `lost_n_found`, `link`, `metawalk`, `util`, and the pass2-populated `dir_info` tree. This pass depends strongly on pass2’s `treewalk_parent` and `dotdot_parent` bookkeeping.

Risks and notes:
- Several comments identify missing interactive policy refinement around choosing parents.
- Parent choice defaults to treewalk when both parents look like directories.
- Some recovery paths remove the dentry from a bad parent and leave the directory unlinked for later lost+found handling.
