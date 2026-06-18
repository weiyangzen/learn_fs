# sources/user-network-fs/go-fuse/fs/dirstream_darwin.go

Purpose: Darwin implementation of the directory-entry syscall adapter.

Important API: `getdents(fd, buf)` calls `unix.Getdirentries(fd, buf, nil)`.

Control flow/state: no retained state; wraps a platform syscall for `dirstream.go`.

Dependencies/integration: selected for Darwin builds; used by `loopbackDirStream.load`. Risks are OS-specific directory entry layout and offset handling differences. Cross-build coverage in `all.bash` is the main signal, but runtime behavior needs macOS-specific tests.
