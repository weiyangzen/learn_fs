# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/internal.h

This header defines the private contract for FSAL_RGW. It ties Ganesha FSAL structures to librgw types and exposes the internal functions used across `main.c`, `handle.c`, `internal.c`, and `up.c`.

Important types are `struct rgw_fsal_module`, the singleton module wrapper containing `struct fsal_module`, the object ops vector, config strings, and `librgw_t`; `struct rgw_export`, containing the public export, `struct rgw_fs`, root handle, and RGW user/access credentials; `struct rgw_handle`, containing the public object handle, librgw file handle, upcall vector, export pointer, share reservation state, and open flags; and `struct rgw_open_state`, embedding a `state_t` plus open flags. Attribute support masks expose POSIX attributes and optionally `ATTR4_XATTR` when `USE_FSAL_RGW_XATTRS` is enabled. The header also enforces a minimum `librgw_file` version at compile time.

State is divided into module-global library state, per-export mount/authentication state, per-object handle state, and per-open state. Wire identity is not defined here directly, but the handle stores `rgw_file_handle`, whose `fh_hk` is used by handle digest and invalidation paths.

Dependencies include Ganesha FSAL headers, `sal_data.h`, uuid/dirent system headers, and Ceph `librgw.h`/`rgw_file.h`. Integration points are the exported prototypes for handle/export ops initialization, state allocation, error conversion, and RGW invalidation upcalls.

Risks include broad sharing of the global `RGWFSM`, credential string lifetimes from config parsing, and coupling to librgw internal handle-key layout. Test signals should include compile coverage for librgw version guards, xattr/non-xattr builds, and ABI-sensitive uses of `struct rgw_fh_hk` in wire handles and upcalls.
