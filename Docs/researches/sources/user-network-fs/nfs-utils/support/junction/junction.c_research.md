# sources/user-network-fs/nfs-utils/support/junction/junction.c

## Purpose
Implements low-level local filesystem operations for junction directories: open/stat, sticky-bit marker handling, trusted xattr access, and saved-mode restore.

## Important APIs, Types, and Functions
Functions include `junction_open_path()`, `junction_is_directory()`, `junction_is_sticky_bit_set()`, `junction_set_sticky_bit()`, xattr present/read/get/set/remove helpers, `junction_get_mode()`, `junction_save_mode()`, and `junction_restore_mode()`.

## Control Flow
Operations open directories with `O_DIRECTORY`, inspect via `fstatat(AT_EMPTY_PATH)`, use no-execute plus sticky bit as a junction marker, store original mode as a trusted xattr, and read/write/remove trusted xattrs by fd.

## State and Persistence Behavior
Persistent state is directory mode bits plus trusted xattrs `trusted.junction.mode` and `trusted.junction.nfs`. Heap buffers returned by read/get helpers are caller-owned.

## Dependencies and Integration Points
Depends on Linux xattr APIs, libjunction internal constants, and `xlog`. Used by NFS junction add/delete/query code and XML helpers.

## Risks and Edge Cases
Trusted xattrs require CAP_SYS_ADMIN. `junction_set_sticky_bit()` clears all permission bits before setting sticky, making restore correctness critical. Error mapping is coarse for xattr set/remove failures.

## Test Signals
Test directory/non-directory paths, permission failures, xattr absent/present, binary and string xattr reads, save/restore mode, read-only filesystem errors, and cleanup after partial add failures.
