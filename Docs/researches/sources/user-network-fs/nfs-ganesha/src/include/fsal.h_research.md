# sources/user-network-fs/nfs-ganesha/src/include/fsal.h

## Purpose
`fsal.h` is the main File System Abstraction Layer public header for Ganesha core code. It declares operation context handling, FSAL module loading/registration/configuration, common FSAL operation wrappers, attribute helpers, async I/O helpers, and FD LRU configuration.

## Important APIs, Types, And Functions
The header declares thread-local `op_ctx`, global `pnfs_fsal`, delegation config tokens, root export options, cluster node identifiers, and context functions such as `init_op_context`, `release_op_context`, `suspend_op_context`, `resume_op_context`, and export/client/pNFS setters. FSAL manager APIs include `load_fsal_static`, `register_fsal`, `unregister_fsal`, `lookup_fsal`, `load_fsal`, `fsal_load_init`, `fsal_init`, `subfsal_commit`, `start_fsals`, `destroy_fsals`, and cleanup routines. Operation helpers wrap access, lookup, create, readdir, remove, rename, open/reopen/close, statfs, commit, verify, read/write, xattr listing, and attribute display/logging.

## Control Flow
During startup/config, `start_fsals` and export parsing load FSAL modules by name. `load_fsal` dlopens module shared objects, resolves `fsal_init` if constructors do not register, and expects `register_fsal` to publish the module with default ops. `fsal_load_init` then calls module `init_config` or `update_config`. Protocol operations set `op_ctx`, then call FSAL wrapper functions that validate common conditions and dispatch through `fsal_obj_handle->obj_ops` or `fsal_module->m_ops`.

## State And Persistence
FSAL module state is process memory: module list under `fsal_lock`, per-module refcounts, operation vectors, server/handle/export lists, dlopen handles, paths, configured flags, and pNFS table entries. `op_ctx` is thread-local and must be set for operations expecting request/export/client credentials. FD LRU state tracks global FD counters and policy parameters. Persistent state belongs to backing filesystems or recovery/config subsystems, not this header.

## Dependencies And Integration Points
It depends on `fsal_api.h`, NFS protocol headers, ACL and fs_locations headers, config parsing, display buffers, and FSAL access-check helpers. It integrates with `FSAL/fsal_manager.c`, `FSAL/commonlib.c`, exports, SAL state code, protocol handlers, pNFS utilities, MDCACHE, recovery, and FSAL plugin modules.

## Risks
`lookup_fsal` sets `op_ctx->fsal_module`, so callers need a valid operation context. Attribute copying has nuanced ownership for ACLs, fs_locations, and security labels; misuse can leak or double-release references. `fsal_close` silently normalizes `ERR_FSAL_NOT_OPENED` for regular files and ignores non-regular files. Dynamic loading is sensitive to generated module paths, lowercase basename conversion, API version checks, and registration state. FD LRU settings influence resource exhaustion behavior.

## Test Signals
Test signals include FSAL dynamic/static load and version mismatch tests, config init/update paths, refcounted lookup/unregister, operation wrapper tests with mock `obj_ops`, attr prepare/copy/release ownership tests, close/commit edge cases, async read/write completion, xattr listing cookie behavior, FD LRU high/low water behavior, and integration tests under FSAL_MEM/VFS/proxy modules.
