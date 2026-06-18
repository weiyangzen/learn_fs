# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.h

This header declares the SaunaFS context wrapper API used by the FSAL implementation. Its purpose is to expose credential-aware operations with Ganesha-friendly signatures while hiding direct `sau_context_t` creation and destruction from handle, export, MDS, and DS code.

The declarations include namespace-like `saunafs_*` functions for metadata operations (`lookup`, `mknode`, `mkdir`, `rmdir`, `unlink`, `rename`, `symlink`, `readlink`, `link`), file operations (`open`, `read`, `write`, `flush`, `fsync`), attribute operations (`getattr`, `setattr`), directory operations (`opendir`, `readdir`), pNFS support (`get_chunks_info`), ACL support (`setacl`, `getacl`), byte-range locking (`setlock`, `getlock`), and xattrs (`getxattr`, `setxattr`, `listxattr`, `removexattr`).

State behavior is implicit in the types: `sau_t` represents a mounted SaunaFS client instance, `struct user_cred` supplies caller credentials, `sau_inode_t` identifies persistent filesystem objects, and `fileinfo_t`/`sau_fileinfo` represent open file or directory state returned by the client library.

Dependencies are `fsal_types.h` and `saunafs_fsal_types.h`, which supplies `fileinfo_t` and SaunaFS types. This header is a major integration boundary between Ganesha's FSAL layer and the SaunaFS client C API.

Risks include declarations that mirror external C API types closely, so client library ABI/API changes ripple into the FSAL. Since errors are mostly raw `int`/pointer returns, callers must consistently use `fsalLastError`, `nfs4LastError`, or `saunafsToFsalError`. Test signals should include compiler coverage against the target SaunaFS client version and caller tests that validate every failure path uses the proper error conversion.
