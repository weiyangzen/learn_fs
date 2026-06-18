# File Research: sources/os/linux/linux-stable/fs/fhandle.c

This file implements the VFS file-handle syscalls: `name_to_handle_at()` encodes a path into a filesystem export handle plus mount ID, and `open_by_handle_at()` decodes such a handle back into an opened file.

Major responsibilities:
- Validate user flags for handle encoding, including `AT_HANDLE_FID`, `AT_HANDLE_CONNECTABLE`, `AT_EMPTY_PATH`, symlink following, and unique mount IDs.
- Call exportfs encode/decode hooks through `exportfs_encode_fh()` and `exportfs_decode_fh_raw()`.
- Copy variable-sized `struct file_handle` payloads safely to and from userspace.
- Resolve the decode anchor from an fd, `AT_FDCWD`, `FD_PIDFS_ROOT`, or `FD_NSFS_ROOT`.
- Enforce permissions for handle decoding, including legacy `CAP_DAC_READ_SEARCH` and newer mount/user-namespace based permission checks.
- Verify connectable handles by checking that decoded dentries are reachable from the supplied root and have valid id mappings.
- Open decoded paths through filesystem-specific export `open()` hooks or `file_open_root()`.

Important design points:
- Encoding rejects filesystems that cannot encode the requested handle type.
- Connectable handles store user-visible type bits (`FILEID_IS_CONNECTABLE`, `FILEID_IS_DIR`) in `handle_type`, then strip those bits before calling filesystem decode logic.
- Decode permission handling is split between optional filesystem export permission hooks and generic `may_decode_fh()`.
- `vfs_dentry_acceptable()` is used as the exportfs acceptability callback and performs subtree/idmapping validation.
- `open_by_handle_at()` follows normal open flag handling, including `O_LARGEFILE` for native syscalls and a compat syscall variant without forced largefile.

Key invariants:
- `handle_bytes` must be nonzero for decode and no larger than `MAX_HANDLE_SZ`.
- Filesystem code must not see VFS/user flag bits embedded in `handle_type`.
- `AT_HANDLE_CONNECTABLE` conflicts with `AT_HANDLE_FID` and `AT_EMPTY_PATH`.
- Relaxed decode permissions require directory-only opens and capability checks sufficient to reach the object through the supplied mount root.
- On overflow or `FILEID_INVALID`, encode reports `-EOVERFLOW` and only copies the fixed handle header back.

External interfaces:
- Defines `name_to_handle_at`, `open_by_handle_at`, and compat `open_by_handle_at`.
- Depends on exportfs operations, mount namespace helpers, pidfs/nsfs roots, VFS open helpers, and userspace copy helpers.
