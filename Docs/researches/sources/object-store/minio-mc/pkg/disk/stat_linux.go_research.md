## sources/object-store/minio-mc/pkg/disk/stat_linux.go

Purpose: Linux implementation of `GetFileSystemAttrs` for preserved filesystem metadata. It uses `os.Stat` and casts `FileInfo.Sys()` to `*syscall.Stat_t`.

Control flow reads stat data, formats `Atim` and `Mtim` seconds/nanoseconds, appends GID, optional group name, mode, UID, and optional user name. State is read-only local file metadata; output is later stored as object metadata. Dependencies are `os`, `syscall`, `os/user`, `strconv`, and `strings.Builder`. Risks include the unchecked type assertion on `Sys()`, omitted lookup names in minimal containers, and no ctime/md5 despite the comment mentioning them. Functional tests include `test_copy_object_preserve_filesystem_attr`, which compares local and remote metadata on the runtime platform.
