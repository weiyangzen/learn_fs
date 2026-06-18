# File Research: sources/os/linux/linux/fs/xfs/scrub/parent.c

## Role
Scrubs parent relationships for XFS inodes. On older filesystems it validates directory `..`; on parent-pointer filesystems it validates xattr parent pointers against forward directory entries.

## Setup
- `xchk_setup_parent` prepares repair if available and sets up inode contents scrub.

## Legacy `..` Validation
- `xchk_parent` rejects non-directories when parent pointers are absent.
- It looks up `..`, validates root/metadir self-parent rules, and checks that the alleged parent directory has exactly the expected dirent pointing back.
- `xchk_parent_validate` handles invalid parent inode numbers, corrupt parent inodes, non-directory parents, zapped directories, and metadata/regular tree crossing.

## Parent Pointer Scrub
- `xchk_parent_pptr` walks parent-pointer xattrs with `xchk_xattr_walk`.
- `xchk_parent_scan_attr` parses each parent record, rejects self-parent pointers, validates parent inode/generation/type, and checks the forward dirent.
- Parent pointers that cannot be checked due to trylock failure are stashed in `xfarray`/`xfblob`.

## Slow Path
- `xchk_parent_finish_slow_pptrs` replays deferred parent pointers.
- `xchk_parent_slow_pptr` revalidates xattrs after lock cycling so stale removed parent pointers are not reported as corruption.
- `xchk_dir_trylock_for_pptrs` is used when the normal fast trylock path fails.

## Directory Consistency
- `xchk_parent_pptr_and_dotdot` verifies a linked directory’s `..` matches at least one parent pointer.
- `xchk_parent_count_pptrs` compares parent-pointer count to link count, with special handling for roots, unlinked directories, and superblock-rooted metadir children.

## Zapped Attr Detection
- `xchk_pptr_looks_zapped` detects missing or reset attr forks that imply parent pointers were zapped by inode repair and should be postponed.
