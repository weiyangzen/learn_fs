# File Research: sources/os/linux/linux/fs/xfs/scrub/orphanage.c

## Role
Implements online repair’s orphanage directory, modeled after `xfs_repair`’s `/lost+found`, and provides adoption helpers for reconnecting orphaned files.

## Orphanage Creation
- `xrep_orphanage_create` locates the root dentry, creates or finds `lost+found`, verifies it is a directory, grabs its inode, and stores it in `sc->orphanage`.
- Read-only filesystems skip creation.
- `xrep_chown_orphanage` makes the orphanage root-owned, clears setuid/setgid/sticky and realtime inheritance flags, and updates quota ownership.

## Locking Helpers
- `xrep_orphanage_ilock`, `xrep_orphanage_ilock_nowait`, and `xrep_orphanage_iunlock` track orphanage lock state in the scrub context.
- `xrep_orphanage_iolock_two` repeatedly trylocks orphanage and scrub target IOLOCKs to avoid blocking while a scrub transaction exists.
- `xrep_orphanage_rele` releases locks and inode references.

## Adoption
- `xrep_orphanage_can_adopt` excludes the orphanage itself, superblock-rooted inodes, and internal inodes.
- `xrep_adoption_trans_alloc` reserves space, locks orphanage and child, joins both inodes, and reserves quota with repair override semantics.
- `xrep_adoption_compute_name` chooses a unique orphanage name based on inode number with numeric suffix fallback.
- `xrep_adoption_move` creates the orphanage dirent, bumps link counts as needed, updates child `..` for directories, adds parent pointers when enabled, emits dirent hook notifications, and invalidates relevant dentries.
- `xrep_adoption_trans_roll` finishes deferred work and rolls to a clean transaction.

## Risk Points
- Dcache checks guard against disagreement between the locked ondisk directory and VFS lookup state.
- Parent-pointer filesystems may need attr fork creation before adoption.
- Adoption returns with a dirty transaction so callers can combine it with other metadata fixes.
