## sources/object-store/minio-mc/pkg/disk/stat_darwin.go

Purpose: Darwin implementation of `GetFileSystemAttrs`, serializing filesystem metadata into the mc metadata attribute string used by preserve-attributes copy flows.

Control flow calls `syscall.Stat`, then appends `atime`, `gid`, optional `gname`, `mode`, `mtime`, `uid`, and optional `uname` using Darwin `Atimespec` and `Mtimespec` fields. State is read-only local filesystem metadata. Dependencies are `syscall`, `os/user`, `strconv`, and `strings.Builder`. Integration is with `mc cp -a` and `parseAttribute`/`parseAtimeMtime`. Risks include user/group lookup failures being silently omitted, platform-specific stat field drift, and no escaping for names containing separators. Tests in this subset only validate parsing, not Darwin stat output.
