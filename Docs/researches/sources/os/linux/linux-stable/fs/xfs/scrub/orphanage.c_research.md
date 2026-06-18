# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/orphanage.c

This file implements online repair’s orphanage mechanism, equivalent in role to `xfs_repair` using `/lost+found`.

Main responsibilities:
- Create or find `/lost+found` at filesystem root.
- Normalize ownership and mode bits of the orphanage.
- Provide lock helpers for the scrub context’s orphanage inode.
- Move damaged or disconnected files into `/lost+found` transactionally.

`xrep_orphanage_create`:
- Rejects shutdown filesystems and no-ops on readonly mounts.
- Uses VFS dentry helpers to find the root dentry.
- Uses `start_creating_noperm` and `vfs_mkdir` to create `lost+found` if needed.
- Requires the result to be a directory.
- Grabs an inode reference and calls `xrep_chown_orphanage`.

`xrep_chown_orphanage`:
- Allocates root user/group/project dquots.
- Clears setuid/setgid/sticky bits.
- Changes uid/gid/projid to root/zero.
- Clears realtime inheritance flags.
- Logs quota and inode changes.

Adoption flow:
- `xrep_orphanage_can_adopt` filters out orphanage itself, root/superblock-rooted files, and internal inodes.
- `xrep_orphanage_iolock_two` obtains orphanage and target IOLOCKs using nonblocking loops because scrub can already hold transactions.
- `xrep_adoption_trans_alloc` allocates a link transaction with space for orphanage entry creation, child `..` replacement if the child is a directory, and parent-pointer attr fork creation if needed.
- `xrep_adoption_compute_name` chooses a unique filename based on inode number, with `.N` suffixes up to 10,000 attempts.
- `xrep_adoption_move` creates the orphanage dirent, updates orphanage link count for child directories, optionally bumps child nlink, replaces child `..`, adds parent pointer records, emits directory update hooks, and invalidates relevant dentries.
- `xrep_adoption_trans_roll` finishes deferred work and rolls to a clean scrub transaction.

Dcache handling:
- Before adoption, `xrep_adoption_check_dcache` ensures there is no positive dentry for the chosen name.
- After adoption, `xrep_adoption_zap_dcache` invalidates negative orphanage dentries and aliases of the moved child.

This code bridges VFS namespace operations with XFS metadata repair, while keeping actual adoption changes in XFS transactions.
