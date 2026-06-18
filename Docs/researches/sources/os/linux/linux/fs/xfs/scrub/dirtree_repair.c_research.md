# File Research: sources/os/linux/linux/fs/xfs/scrub/dirtree_repair.c

## Role
Repairs directory tree structural problems found by `dirtree.c`. It removes unwanted parent links that create cycles or multiple parent paths, and can reattach orphaned directories to the orphanage.

## Decision Logic
- `xrep_dirtree_decide_fate` evaluates current paths and chooses actions:
  - Parentless directories delete all paths.
  - Directories with exactly one good or suspect path keep it.
  - Directories with zero acceptable paths request orphanage adoption.
  - Directories with multiple paths keep one good path if available, otherwise one suspect path, and mark the rest for deletion.
- Helpers retain the surviving parent inode so `..` can be corrected when deleting other paths.

## Deleting Bad Paths
- `xrep_dirtree_prep_path` loads the first path step and name.
- `xrep_dirtree_delete_path` drops scan resources, igets the parent, and calls `xrep_dirtree_unlink`.
- `xrep_dirtree_unlink` locks parent and child IOLOCKs, allocates a remove transaction, checks for stale scan data, updates path state, adjusts `..` if needed, drops link counts, removes the parent directory entry, removes the parent pointer, notifies dir hooks, purges the VFS dentry, and commits.
- `xrep_dirtree_purge_dentry` deletes cached child dentries under the old parent.

## Adoption
- `xrep_dirtree_adopt` locks the orphanage and child, allocates adoption transaction resources, computes an orphanage name, creates an in-progress adoption path for live hook visibility, moves the directory, and commits.
- `xrep_dirtree_move_to_orphanage` drops current scan resources, performs adoption, then reacquires the empty transaction, target ILOCK, and scan lock.

## Top-Level Repair
- `xrep_dirtree` acquires the dirtree scan lock, decides fate if current data are not stale, applies repairs, and reruns path discovery when repair returns `-ESTALE`.
- Path depth/count overflow becomes corruption during repair.

## Invariants and Concurrency
- Lock acquisition follows IOLOCK, transaction, ILOCK, scan-lock ordering.
- The target directory IOLOCK is preserved across operations that need to serialize with namespace changes, but ILOCK and transactions are dropped/reacquired around operations with their own reservation requirements.
- Live directory hooks are notified for repair changes so scanner state can transition rather than falsely invalidating itself.
