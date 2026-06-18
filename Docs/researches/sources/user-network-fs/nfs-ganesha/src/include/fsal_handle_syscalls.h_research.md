# sources/user-network-fs/nfs-ganesha/src/include/fsal_handle_syscalls.h

Purpose: This header abstracts platform-specific by-handle filesystem syscalls for VFS-style FSAL handle creation/opening.

Important APIs/types/functions: `VFS_HANDLE_LEN` fixes the maximum opaque VFS handle payload at 59 bytes. `vfs_file_handle_t` stores a one-byte `handle_len` plus handle bytes; the length byte is not sent on the wire. `vfs_handle_invalid` rejects oversized `gsh_buffdesc` values. `vfs_alloc_handle` allocates and initializes a stack handle via `alloca`; `vfs_malloc_handle` allocates the same shape with `gsh_calloc`.

Control flow: Callers allocate a handle wrapper, platform headers supply Linux or FreeBSD syscall definitions, and FSAL code uses those functions to convert between file handles and opened files. Compile-time platform selection includes `os/linux/fsal_handle_syscalls.h` or `os/freebsd/fsal_handle_syscalls.h`.

State and persistence: The header itself owns no durable state. The serialized handle bytes are persistent identity material for VFS file handles and must remain within `VFS_HANDLE_LEN`.

Dependencies and integration points: It depends on `config.h`, POSIX headers, `gsh_types.h`, and platform syscall headers. It is intentionally top-level even though the TODO says it belongs under FSAL_VFS.

Risks: Oversized handles cause invalidation; too-small limits can break filesystems with larger native handles. Stack allocation via `alloca` must stay scoped. Compile guards fail builds on unsupported or very old platforms without `AT_FDCWD`.

Test signals: Build on Linux/FreeBSD, verify unsupported-platform failure, test valid and oversized descriptors, ensure zero initialization and `handle_len` setup, and run VFS handle open-by-handle regression tests.
