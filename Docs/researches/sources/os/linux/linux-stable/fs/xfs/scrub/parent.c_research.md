# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/parent.c

This file scrubs parent relationships.

There are two modes:
- Without parent pointers: only directories are checked by validating `..` against a real parent directory entry.
- With parent pointers: every parent-pointer xattr is checked against the alleged parent directory’s forward dirent.

Setup:
- `xchk_setup_parent` optionally prepares repair and then sets up inode-content scrub.

Legacy `..` checking:
- `xchk_parent` looks up `..` for directories.
- `xchk_parent_validate` handles root and metadata-root self-parenting, rejects self-parenting for ordinary directories, igets the alleged parent, verifies it is a directory in the same tree, and walks the parent directory to count entries pointing to the child.
- Linked directories expect exactly one forward entry; unlinked directories expect zero.
- Lock contention returns `-EAGAIN` so the caller can revalidate.

Parent-pointer checking:
- `xchk_parent_pptr` allocates scratch `xfarray`/`xfblob` storage for deferred parent pointers.
- `xchk_parent_scan_attr` walks xattrs, filters `XFS_ATTR_PARENT`, decodes records, rejects self-references, validates alleged parent inode/generation, and checks the parent dirent.
- If parent locking fails, it saves the pointer/name into scratch storage.
- `xchk_parent_finish_slow_pptrs` later rechecks deferred pointers, cycling locks if needed via `xchk_dir_trylock_for_pptrs`.
- If locks were cycled, `xchk_parent_revalidate_pptr` confirms the parent pointer still exists before using it.

Additional checks:
- For directories, `xchk_parent_pptr_and_dotdot` ensures `..` matches at least one parent pointer unless the directory is root or unlinked.
- `xchk_parent_count_pptrs` compares parent-pointer count to link count:
  - non-directories should match exactly,
  - linked directories should have at least one,
  - unlinked directories should have none,
  - superblock-rooted metadata children get special treatment.

`xchk_pptr_looks_zapped` detects cases where parent-pointer attrs are unavailable because inode/ifork repair zapped the attr fork. This lets other scrubbers postpone parent-pointer conclusions instead of reporting false corruption.
