# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_rename.c

## Summary
Implements msdosfs rename using NetBSD's `genfs_sane_rename` framework. It adapts the old VOP rename API to a saner internal flow, provides filesystem-specific permission and genealogy callbacks, creates the destination directory entry, removes the source entry, rekeys denodes, and fixes `..` for reparented directories.

## Main Responsibilities
- Normalize VFS rename arguments in `msdosfs_rename()`, unlocking/releasing nodes according to the caller contract and rejecting invalid target-directory self-renames.
- Delegate high-level ordering, locking, and validation to `genfs_sane_rename()` with msdosfs callback operations.
- Model FAT permissions as UFS-like modes based on mount owner, masks, and the DOS readonly bit.
- Check whether target directories are empty with `msdosfs_dosdirempty()`.
- Perform actual renames in `msdosfs_gro_rename()` by optionally removing the target, generating the destination 8.3 name, creating a new directory entry, incrementing `de_refcnt`, removing the old entry, and rekeying non-directory vcache entries.
- Handle same-object remove cases with `msdosfs_gro_remove()`.
- Re-run lookup and preserve `msdosfs_lookup_results` in `msdosfs_gro_lookup()`.
- Walk parent chains in `msdosfs_gro_genealogy()` using `..` entries to prevent directory cycles.
- Read and replace `..` entries with `msdosfs_read_dotdot()` and `msdosfs_rename_replace_dotdot()`.
- Lock directories safely for rename traversal with `msdosfs_gro_lock_directory()`.

## Key Interfaces
- `msdosfs_rename(void *)`.
- Static `msdosfs_sane_rename(...)`.
- Static `msdosfs_gro_rename(...)`, `msdosfs_gro_remove(...)`, `msdosfs_gro_lookup(...)`, and `msdosfs_gro_genealogy(...)`.
- Static `msdosfs_read_dotdot(...)` and `msdosfs_rename_replace_dotdot(...)`.
- `msdosfs_genfs_rename_ops`, the callback table passed to `genfs_sane_rename()`.

## Risks
The implementation explicitly notes non-journaled crash-consistency gaps: if a crash occurs after target removal or after destination creation but before source removal, POSIX rename guarantees may be violated. Several failure paths contain comments questioning whether rollback or panic is appropriate. Directory rename uses the legacy `DE_RENAME` guard, and parent-chain analysis trusts on-disk `..` entries. The code has to compensate for VFS rename API locking/reference conventions, making lock ordering and reference ownership important.
