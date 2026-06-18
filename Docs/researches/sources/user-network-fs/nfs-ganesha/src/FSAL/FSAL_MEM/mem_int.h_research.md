# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_int.h

## Purpose
`mem_int.h` is the private interface for FSAL_MEM. It defines the in-memory export, object, dirent, state, module, async mode, and package/export/handle/upcall function contracts shared by MEM source files.

## Important APIs, Types, And Functions
`enum async_types` defines `MEM_INLINE`, `MEM_RANDOM_OR_INLINE`, `MEM_RANDOM`, and `MEM_FIXED` for test I/O completion behavior. `struct mem_fsal_export` embeds `struct fsal_export`, stores the export path/root handle, links into `MEM.mem_exports`, protects the per-export object list with `mfe_exp_lock`, and carries async delay/stall/type configuration. `struct mem_state_fd` prepends `struct state_t` so default state freeing can work and adds a per-state `struct fsal_fd`.

`struct mem_fsal_obj_handle` embeds `struct fsal_obj_handle`, cached POSIX attributes, fileid, fixed wire handle, type-specific unions for directory/file/node/symlink state, reverse dirent list, export list entry, owning export pointer, debug name, data capacity, export-root flag, explicit refcount, and flexible file data storage. `struct mem_dirent` links a child handle to a directory by name and cookie/index with AVL nodes and a reverse-list node. The header declares `mem_handle_ops_init()`, `mem_create_export()`, `mem_update_export()`, `str_async_type()`, `mem_clean_export()`, `mem_clean_all_dirents()`, `mem_up_pkginit()`, `mem_up_pkgshutdown()`, and the export lookup/create-handle methods.

## Control Flow
The header establishes the object ownership model used by `mem_handle.c` and `mem_export.c`. Export creation allocates `mem_fsal_export`, initializes the root lazily through `mem_lookup_path()`, and appends exports to `MEM.mem_exports`. Object operations use the embedded `fsal_obj_handle` for upper-layer dispatch and the private union for actual in-memory behavior. Directory traversal and mutation are expressed through `mem_dirent` entries in the parent AVL trees and child reverse lists.

## State And Persistence
All declared state is memory-resident. The only long-lived structures are module globals and export/object lists inside the running process. `V4_FH_OPAQUE_SIZE` fixes MEM file-handle size to 58 bytes. `mem_free_handle()` removes an object from the export object list, clears the owning export pointer and debug name, and frees the object; callers must hold `mfe_exp_lock` for write.

## Dependencies And Integration Points
The header depends on Ganesha AVL/list primitives, FSAL types, optional LTTng trace definitions, pthread rwlocks, and MEM-specific package globals. It is included by MEM handle, export, main, and upcall implementations. The `extern struct mem_fsal_module MEM` global is the module-wide control block registered with Ganesha.

## Risks
Correctness relies on lock ordering documented outside the type definitions: object locks for trees/reverse lists and export locks for object-list lifetime. Because `mem_fsal_obj_handle` has a flexible `data[0]` tail and file capacity is configured globally, callers must not assume data length follows file size. `mem_free_handle()` is inline and destructive, so misuse without the export write lock can corrupt the export object list.

## Test Signals
Compile-time signals include all MEM sources agreeing on struct layout, especially `mem_state_fd` with `state` first. Runtime signals include export cleanup freeing all object list entries, no stale reverse dirents after unlink/rename, and async/upcall configuration being visible across MEM source files.
