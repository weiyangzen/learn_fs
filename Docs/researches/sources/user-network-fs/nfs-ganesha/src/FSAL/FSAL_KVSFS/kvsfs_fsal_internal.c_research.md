## sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_fsal_internal.c

Purpose: This small translation unit owns the definition of KVSFS module-global filesystem information declared in the internal header. It exists to provide one storage location for `global_fs_info`.

Important APIs and types: The only exported object defined here is `struct fsal_staticfsinfo_t global_fs_info;`. The `FSAL_INTERNAL_C` macro is defined before including `kvsfs_fsal_internal.h` so the header suppresses its `extern` declarations guarded by `#ifndef FSAL_INTERNAL_C`.

Control flow and state: There is no executable control flow. State consists of the mutable global `global_fs_info`, with comments saying access is thread-safe because it is read-only except during initialization.

Persistence behavior: No persistent storage is touched. The object is process-global runtime state that should be initialized once and then treated as read-only by KVSFS code.

Dependencies and integration points: It includes `config.h`, `fsal.h`, `kvsfs_fsal_internal.h`, `abstract_mem.h`, and `pthread.h`. Other KVSFS files include the internal header and reference `global_fs_info` as an external symbol. The broader module initialization path likely copies or derives FSAL static capabilities from this object.

Risks: Because `global_fs_info` is writable C global storage, the claimed thread safety depends on discipline outside this file. If initialization and access overlap, there is no lock here. Test signals are mostly link/build checks ensuring exactly one definition exists, plus module initialization tests verifying the global is fully populated before exports or object ops read it.
