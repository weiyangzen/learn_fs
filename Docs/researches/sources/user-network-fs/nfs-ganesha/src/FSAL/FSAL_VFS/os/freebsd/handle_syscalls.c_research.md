# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/freebsd/handle_syscalls.c

Purpose: this file implements FreeBSD-specific persistent handle operations using `getfhat`, `fhopen`, and FreeBSD file-handle structures.

Important functions: `vfs_sizeof_handle` computes packed handle length from `v_fhandle`. `display_vfs_handle` logs fsid and fid details. `vfs_fd_to_handle` and `vfs_name_to_handle` call `getfhat` with follow/no-follow flags. `vfs_open_by_handle` calls `fhopen` and maps `ENOENT` to `ESTALE`. `vfs_extract_fsid` extracts `FSID_TWO_UINT32`. `vfs_encode_dummy_handle` encodes a filesystem fsid into fid data, marks `fh_flags` as `HANDLE_DUMMY`, and sets reserved fsid type metadata. `vfs_is_dummy_handle` and `vfs_valid_handle` classify and validate handles. `vfs_re_index` obtains the root handle, extracts its fsid, and reindexes the Ganesha filesystem registry.

Control flow and state: persistent handle bytes are FreeBSD `v_fhandle` bytes. On filesystem claim, reindexing aligns Ganesha's fsid with the fsid embedded in FreeBSD handles.

Dependencies and integration points: depends on FreeBSD mount/fhandle APIs, `syscalls.h`, FSAL fsid encoding helpers, and VFS common methods. Used through the common syscall interface by export and handle code.

Risks: handle length must fit `VFS_HANDLE_LEN`; the compile-time check guards `MAXFIDSZ`. Dummy handles use special `fh_flags` and encoded fsid in fid data; validation must reject malformed lengths. `fhopen` errors drive stale-handle behavior.

Test signals: create handles for root, files, directories, symlinks; reopen by handle; stale deleted handles; dummy handle encode/validate; fsid reindex on export claim; invalid length/fid cases.
