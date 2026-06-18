# sources/user-network-fs/go-fuse/fs/dirstream_unix.go

Purpose: non-Darwin implementation of the directory-entry syscall adapter.

Important API: build-tagged `!darwin`; `getdents(fd, buf)` calls `unix.Getdents`.

Control flow/state: no state; wraps syscall for `loopbackDirStream`.

Dependencies/integration: used on Linux and other non-Darwin Unix platforms. Risks include differences on FreeBSD or unsupported platforms under the broad `!darwin` tag, but package cross-builds and platform-specific files reduce that. Runtime tests on Linux cover the common path.
