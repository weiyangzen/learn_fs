# File Research: sources/os/linux/linux/fs/namei.c

## Purpose
Implements Linux VFS pathname resolution and many pathname-based filesystem operations. It covers filename copying, permission checks, RCU/ref path walking, symlink traversal, mount traversal, lookup helpers, open/create logic, and syscall-level implementations for mknod, mkdir, rmdir, unlink, symlink, link, rename, and readlink-related helpers.

## Main Responsibilities
- Copy user/kernel pathnames into `struct filename` objects.
- Perform DAC, ACL, capability, idmapped mount, device-cgroup, and LSM permission checks.
- Walk paths using RCU-walk fast paths and ref-walk fallback.
- Cross mountpoints, automounts, and `..` across mount roots.
- Enforce scoped lookup flags such as `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_NO_XDEV`, `LOOKUP_NO_SYMLINKS`, and `LOOKUP_NO_MAGICLINKS`.
- Resolve symlinks iteratively with bounded stack depth and total link count.
- Provide in-kernel lookup helpers for one-component lookup and full path lookup.
- Provide directory-operation locking helpers.
- Implement VFS create/remove/link/rename primitives and syscall wrappers.
- Provide generic page-cache symlink helpers.

## Major Data Structures
- `struct filename`: allocated from `names_cache`, can embed short names in `iname` or allocate long names separately.
- `struct nameidata`: carries the current path, root, current inode, lookup flags/state, sequence counters, symlink stack, final component, dirfd, and directory owner/mode snapshots.
- `enum last_type`: classifies final/current component as normal, root, `.`, or `..`.
- Symlink stack entries store saved path, delayed cleanup callback, remaining name, and sequence number.

## Filename Handling
- `filename_init()` creates the filename slab cache.
- `do_getname()` copies user pathnames, rejects empty paths unless `LOOKUP_EMPTY`, and switches to heap storage for long paths.
- `getname_flags()`, `getname_uflags()`, and `__getname_maybe_null()` are user-path wrappers.
- `do_getname_kernel()` handles kernel strings.
- `putname()` releases embedded or separately allocated filename storage.
- Delayed filename helpers allow deferring audit completion.

## Permission Model
- `check_acl()` and `acl_permission_check()` combine POSIX ACL checks with UNIX mode-bit checks and idmapped ownership conversion.
- `generic_permission()` adds capability overrides, with directory-specific handling for search/read.
- `do_inode_permission()` caches the fast generic-permission path in `IOP_FASTPERM`.
- `sb_permission()` rejects writes to read-only superblocks for regular files, directories, and symlinks.
- `inode_permission()` adds immutable/unmapped-ID write checks, device cgroup checks, and LSM permission checks.
- `lookup_inode_permission_may_exec()` is a directory traversal-optimized execute/search permission path.

## Path Walking
- `path_init()` chooses the starting path from root, cwd, dirfd, or provided root and initializes RCU/ref walking state.
- `link_path_walk()` parses components, checks traversal permission, hashes names, handles dots, follows intermediate symlinks, and records final component metadata.
- `lookup_fast()` performs dcache lookup and revalidation, staying in RCU mode when possible.
- `lookup_slow()` and `__lookup_slow()` allocate/lookup dentries under directory inode locks.
- `step_into()` advances to a child dentry, crossing mounts or following symlinks as required.
- `complete_walk()` finalizes RCU walks, performs scoped lookup containment validation, and weak revalidation after jumps.
- `try_to_unlazy()` and `try_to_unlazy_next()` convert RCU-walk state to ref-walk state when blocking or references are needed.
- `terminate_walk()` drops paths, symlink callbacks, and RCU state.

## Mount Traversal
- `follow_up()` moves from a mounted filesystem root to the mountpoint in the parent mount.
- `choose_mountpoint_rcu()` / `choose_mountpoint()` select parent mountpoints while handling bind-mount roots.
- `follow_automount()` triggers automounts when lookup intent requires it.
- `traverse_mounts()` and `__traverse_mounts()` cross mounted dentries, call filesystem `d_manage()`, handle automounts, and enforce `LOOKUP_NO_XDEV`.
- `follow_down_one()` and `follow_down()` are exported helpers for descending into covering mounts.
- RCU mount traversal uses `__follow_mount_rcu()`.

## Symlink Handling
- `reserve_stack()` enforces `MAXSYMLINKS` and expands from embedded to allocated symlink stack storage.
- `pick_link()` checks symlink policy, protected symlink rules, `MNT_NOSYMFOLLOW`, LSM follow-link permission, atime updates, magic-link restrictions, absolute symlink root jumps, and delayed cleanup.
- `put_link()` releases the most recent symlink stack entry.
- `may_follow_link()` enforces `protected_symlinks` for sticky world-writable directories.
- `vfs_readlink()`, `vfs_get_link()`, `page_get_link()`, `page_readlink()`, and `page_symlink()` implement common symlink read/write helpers.

## Name Hashing
- With `CONFIG_DCACHE_WORD_ACCESS`, `full_name_hash()`, `hashlen_string()`, and `hash_name()` use word-at-a-time hashing and delimiter detection.
- Without it, byte-at-a-time fallback hashing is used.
- `hash_name()` also detects `.` and `..` through `lastword`.

## Lookup Entry Points
- `filename_lookup()` performs full lookup with RCU first, then ref-walk retry on `-ECHILD`, and revalidation retry on `-ESTALE`.
- `filename_parentat()` and `__filename_parentat()` return parent path plus final component.
- `kern_path()`, `kern_path_parent()`, `vfs_path_lookup()`, and `vfs_path_parent_lookup()` are kernel-facing wrappers.
- One-component helpers include `lookup_one()`, `lookup_one_unlocked()`, positive-only variants, and no-permission variants.
- `lookup_noperm_common()` rejects empty, dot/dotdot, slash, and NUL-containing component names and calls filesystem `d_hash()` when present.

## Directory Operation Locking Helpers
- `start_dirop()` / `end_dirop()` lock parent directories and perform final lookup.
- `start_creating*()` and `start_removing*()` variants combine component validation, optional permission checks, locking, and lookup.
- `start_creating_dentry()` and `start_removing_dentry()` validate an already supplied child dentry.
- Rename setup helpers lock parent directories with deadlock-aware ordering and ancestor trap detection:
  - `lock_rename()`, `lock_rename_child()`, `unlock_rename()`.
  - `start_renaming()`, `start_renaming_dentry()`, `start_renaming_two_dentries()`, and `end_renaming()`.

## Create/Open Path
- `vfs_prepare_mode()` strips SGID/umask and applies VFS type/permission masks.
- `vfs_create()` performs create permission/security checks, delegation breaking, filesystem `->create()`, and fsnotify.
- `may_open()` validates file type, device/noexec restrictions, permissions, append-only rules, and `O_NOATIME`.
- `lookup_open()` handles last-component lookup, creation permission, atomic open, and fallback `->lookup()`/`->create()`.
- `open_last_lookups()` handles RCU fast lookup, creation locking, delegation retry, and transition into final path.
- `do_open()` completes the walk, handles `O_EXCL`, sticky create protections, `O_DIRECTORY`, `O_TRUNC`, `vfs_open()`, LSM post-open, and truncation.
- `vfs_tmpfile()`, `kernel_tmpfile_open()`, `do_tmpfile()`, and `do_o_path()` implement tmpfile and `O_PATH`.
- `path_openat()`, `do_file_open()`, and `do_file_open_root()` are main open entry points.

## Filesystem Mutation Primitives and Syscalls
- Creation:
  - `filename_create()`, `start_creating_path()`, `end_creating_path()`, `start_creating_user_path()`, and `dentry_create()`.
  - `vfs_mknod()`, `filename_mknodat()`, `mknodat`, `mknod`.
  - `vfs_mkdir()`, `filename_mkdirat()`, `mkdirat`, `mkdir`.
- Removal:
  - `may_delete_dentry()` centralizes unlink/rmdir victim checks.
  - `vfs_rmdir()`, `filename_rmdir()`, `rmdir`.
  - `vfs_unlink()`, `filename_unlinkat()`, `unlinkat`, `unlink`.
- Symlink and hardlink:
  - `vfs_symlink()`, `filename_symlinkat()`, `symlinkat`, `symlink`.
  - `may_linkat()`, `safe_hardlink_source()`, `vfs_link()`, `filename_linkat()`, `linkat`, `link`.
- Rename:
  - `vfs_rename()` performs permission/security checks, delegation breaking, locking of source/target inodes, loop/mountpoint/swapfile/max-link checks, filesystem `->rename()`, dcache move/exchange, and fsnotify.
  - `filename_renameat2()`, `renameat2`, `renameat`, and `rename`.

## Security and Hardening Features
- Sysctls:
  - `protected_symlinks`
  - `protected_hardlinks`
  - `protected_fifos`
  - `protected_regular`
- Sticky directory protections:
  - `may_follow_link()` restricts unsafe symlink following.
  - `may_create_in_sticky()` restricts opening existing FIFO/regular files in sticky writable directories.
  - `__check_sticky()` and `may_delete_dentry()` enforce sticky deletion rules.
- Hardlink protections:
  - `may_linkat()` blocks unsafe hardlinks unless owner/capable or source is safe.
- Scoped lookup:
  - `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_NO_XDEV`, and related flags prevent root/mount/symlink escapes.
- LSM hooks are invoked throughout lookup, create, open, symlink, link, rename, readlink, unlink, mkdir, rmdir, and mknod paths.

## Important Behaviors and Edge Cases
- RCU-walk failures return `-ECHILD` and are retried in ref-walk mode.
- Stale dentries returning `-ESTALE` are retried with `LOOKUP_REVAL`.
- `LOOKUP_CACHED` requires RCU and fails with `-EAGAIN` if used alone.
- Empty paths require `LOOKUP_EMPTY`/`AT_EMPTY_PATH`.
- `..` handling respects bind-mount roots and scoped lookup constraints.
- `LOOKUP_NO_XDEV` blocks mount crossing and automount triggering.
- `MNT_NOSYMFOLLOW` and `LOOKUP_NO_SYMLINKS` reject symlink traversal with `-ELOOP`.
- `O_CREAT` lookup intentionally delays some write errors to preserve correct error precedence.
- Truncation for `O_TRUNC` is performed after open permission checks and with write access held.
- Rename locking carefully avoids directory loops and deadlocks with `s_vfs_rename_mutex`.
- `vfs_rename()` skips VFS `d_move()`/`d_exchange()` if the filesystem advertises `FS_RENAME_DOES_D_MOVE`.
- Page-cache symlink helpers require non-highmem mappings for direct folio address access.

## Dependencies
- Dcache, inode, mount, namespace, RCU, seqlock, audit, fsnotify, LSM, POSIX ACL, file locking/delegation, device cgroup, user namespace/idmapping, and page-cache infrastructure.
- Private mount internals from `mount.h`.

## Research Notes
This file is one of the VFS core files. Its most important architectural split is between fast RCU path walking and slower refcounted walking, with careful fallback points whenever filesystem callbacks, blocking, automounts, sequence mismatches, or symlink operations require stronger references.
