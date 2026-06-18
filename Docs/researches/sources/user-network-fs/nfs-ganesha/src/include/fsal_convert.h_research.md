# sources/user-network-fs/nfs-ganesha/src/include/fsal_convert.h

Purpose: This header defines conversion helpers between POSIX/kernel filesystem representations and FSAL-neutral types.

Important APIs/types/functions: `posix2fsal_error` and inline `posix2fsal_status` convert `errno` to `fsal_status_t`. `fsal2posix_openflags`, `fsal2posix_testperm`, `posix2fsal_attributes`, and `posix2fsal_attributes_all` bridge flags, permission checks, and `struct stat`. Inline `fsal2unix_mode`, `unix2fsal_mode`, and `posix2fsal_time` mask mode bits and build `timespec`. `posix2fsal_type`, `posix2fsal_fsid`, `posix2fsal_devt`, and `object_file_type_to_str` cover object type, fsid/device encoding, and diagnostics.

Control flow: VFS-like FSALs call these helpers after syscalls or before issuing POSIX operations. Attribute conversion fills an `fsal_attrlist` and sets masks that upper FSAL/cache/protocol layers consume.

State and persistence: It does not own persistent state, but its mapping decisions affect persistent NFS file attributes, fsids, device ids, and status propagation.

Dependencies and integration points: Depends on `sys/stat.h`, `unistd.h`, and `fsal_types.h`. It is used by POSIX-backed FSALs, object creation, getattr, permission checks, and error translation into NFS replies.

Risks: Incomplete errno mapping can leak wrong NFS status. Mode conversion intentionally strips file type bits via `S_IALLUGO`; callers must not expect it to preserve `S_IFMT`. Attribute masks must match filled fields or cache/protocol code may trust uninitialized data.

Test signals: Validate errno-to-FSAL mapping, open flag conversion, permission mask conversion, all POSIX file type mappings, device/fsid round trips, and stat-to-attr conversion for regular files, directories, symlinks, and special nodes.
