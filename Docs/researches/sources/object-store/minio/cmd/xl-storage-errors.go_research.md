# sources/object-store/minio/cmd/xl-storage-errors.go

Small syscall/OS error classifier library for storage code. Helpers identify no space, invalid argument, I/O, is-dir, not-dir, name-too-long, too-many-symlinks, not-empty, path-not-found, invalid Windows handle, cross-device, too-many-files, not-exist, permission/read-only, and exists conditions.

There is no state. The functions depend on `errors.Is`/`errors.As`, `os`, `runtime`, `syscall`, and `globalWindowsOSName`.

Risks are mostly platform-specific errno mapping, particularly Windows `0x91`, `0x03`, `0x6`, and Solaris `EEXIST` as not-empty. Tests cover only a subset.
