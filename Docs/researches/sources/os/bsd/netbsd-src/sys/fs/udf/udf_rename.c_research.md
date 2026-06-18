# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_rename.c

Read completely: 683 lines.

Implements UDF rename using NetBSD’s `genfs_sane_rename` framework. `udf_rename()` adapts the legacy VOP rename API through `genfs_insane_rename()`, while `udf_sane_rename()` provides the saner internal call into the UDF-specific `genfs_rename_ops` table.

The callback table supplies directory-empty checks, permission checks, actual rename/remove operations, lookup, genealogy analysis, and directory locking. Empty-directory checks populate/use UDF dirhash state. Permission checks map UDF ownership/access modes into the generic UFS-like rename/remove permission helpers.

`udf_gro_rename()` performs the core operation: gather source attributes, detach an existing target if present, attach the source node under the target name, detach the old source entry, update the moved directory’s `..` entry when reparenting a directory, and purge name-cache state. Rollback attempts reattach/detach if later steps fail. `udf_gro_remove()` handles the same-object rename-over-self case by detaching the original link and reporting the remaining link count.

`udf_gro_lookup()` performs directory lookup by name and returns the vnode found by ICB location. `udf_gro_genealogy()` walks `..` entries from the target directory toward root to detect whether the source directory is an ancestor, preventing directory cycles. `udf_gro_lock_directory()` locks a directory and fails if it has already been removed.

Risk centers on non-journaled rename ordering. The attach/detach/update-`..` sequence has rollback attempts but cannot provide full crash atomicity. Genealogy relies on valid on-disc `..` entries, and dirhash population failures conservatively report directories as non-empty.
