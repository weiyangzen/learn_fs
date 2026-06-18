# sources/user-network-fs/samba/source3/modules/lib_vxfs.c

## Purpose
Runtime wrapper around Veritas VxFS xattr and writeable-xattr helpers from `/usr/lib64/vxfsmisc.so`. It lets Samba VFS code call VxFS-specific APIs when the library is present while returning standard errno-style failures when unavailable.

## APIs, Types, And Control Flow
The file defines function pointers for `vxfs_nxattr_set`, `vxfs_nxattr_get`, `vxfs_nxattr_remove`, `vxfs_nxattr_list`, `vxfs_wattr_set`, and `vxfs_wattr_check`. Public wrappers are fd and path variants for set/get/remove/list xattrs plus set/check writeable xattr state. Path variants open files or directories, call the fd wrapper, and close the descriptor. `vxfs_init()` lazily `dlopen`s the library and resolves all symbols with `dlsym`.

## State, Dependencies, Integration
State is process-local static function pointers and a static library handle. The persistent state affected is filesystem xattr data and VxFS writeable-xattr metadata. It depends on `dlopen`, POSIX `open/close`, `vfs_vxfs.h`, and the external Veritas library. Integration is through VxFS-specific VFS modules.

## Risks And Test Signals
Missing symbols are treated as nonfatal at init and later return `ENOSYS`, which is useful but can delay diagnostics. Path wrappers open non-directories with `O_WRONLY` for mutating operations and `O_RDONLY` for reads, so permission behavior differs from fd callers. Test signals include absent library, partially missing symbols, EFBIG to ERANGE mapping, directory path operations, close-after-error behavior, and errno preservation for returned VxFS error codes.
