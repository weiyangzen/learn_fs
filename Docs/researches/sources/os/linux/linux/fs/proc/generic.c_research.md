# File Research: sources/os/linux/linux/fs/proc/generic.c

## Purpose
Provides generic procfs directory-entry infrastructure: `struct proc_dir_entry` allocation/freeing, name lookup, rb-tree child management, dynamic inode allocation, proc entry registration/removal, and helper APIs for creating proc files, directories, symlinks, seq files, and single files.

## Main Responsibilities
- Maintains each proc directory’s children in an rb-tree under `proc_subdir_lock`.
- Allocates dynamic proc inode numbers from an IDA range.
- Implements generic proc lookup and readdir over `proc_dir_entry` trees.
- Defines generic proc directory/file inode operations.
- Creates and registers proc symlinks, directories, mount points, regular entries, seq entries, and single entries.
- Removes individual proc entries or entire subtrees with rundown and refcount release.
- Provides helpers to set proc entry size, ownership, and permanent status.

## Key Interfaces
- Lookup/readdir: `proc_lookup_de()`, `proc_lookup()`, `proc_readdir_de()`, `proc_readdir()`.
- Registration/creation: `proc_register()`, `proc_symlink()`, `_proc_mkdir()`, `proc_mkdir_data()`, `proc_mkdir_mode()`, `proc_mkdir()`, `proc_create_mount_point()`, `proc_create_reg()`, `proc_create_data()`, `proc_create()`, `proc_create_seq_private()`, `proc_create_single_data()`.
- Removal/lifetime: `pde_put()`, `remove_proc_entry()`, `remove_proc_subtree()`, `proc_remove()`.
- Metadata: `proc_set_size()`, `proc_set_user()`, `proc_get_parent_data()`, `proc_simple_write()`, `impl_proc_make_permanent()`.

## Control Flow and Data Handling
Creation resolves slash-separated names with `xlate_proc_name()`, validates final component names, allocates a `proc_dir_entry`, stores names inline when small, inherits parent ownership, and registers the entry into the parent rb-tree. Registration allocates a dynamic proc inode number and increments parent link count.

Lookup searches the rb-tree, takes a PDE reference, creates an inode with `proc_get_inode()`, and splices it into dcache with appropriate dentry operations. Readdir walks the rb-tree in sorted order and emits entries by stored inode number and mode.

Removal erases entries from parent rb-trees under write lock, rejects permanent entries, runs `proc_entry_rundown()`, warns on non-empty single-entry removal, and releases PDE references. Subtree removal walks descendants depth-first.

## Dependencies and Integration
Used across procfs and by many kernel subsystems that call proc creation APIs. Integrates with proc inode creation, dcache operations, seq_file, IDA allocation, rbtrees, module lifetime/rundown, and proc root state.

## Concurrency and Lifetime Notes
`proc_subdir_lock` protects tree lookup/insertion/removal. PDE refcounts protect entries while lookups/readdir temporarily drop the tree lock. Removal calls rundown so openers complete safely before final release. Permanent entries cannot be removed.

## Risks and Review Hotspots
- Tree/refcount/rundown ordering is critical for module unload safety.
- Name validation prevents collisions with dynamic PID directories at `/proc` root.
- `pidonly` mounts hide generic proc entries and must be respected in lookup/readdir.
- Subtree removal can abort on permanent descendants after partial unlinking, so callers must avoid mixed permanent/removable trees.
