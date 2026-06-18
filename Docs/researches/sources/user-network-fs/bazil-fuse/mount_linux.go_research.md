# sources/user-network-fs/bazil-fuse/mount_linux.go

Purpose: This file implements Linux mounting through the `fusermount3` helper and receives the opened `/dev/fuse` fd over a Unix socket.

Important APIs, types, and functions: `handleFusermountStderr` ignores a common `/etc/fuse.conf` permission warning and parses missing mountpoint errors into `MountpointDoesNotExistError`. `isBoringFusermountError` recognizes helper exit status 1. `mount(dir, conf)` creates a socketpair, starts `fusermount3 -o <opts> -- <dir>` with `_FUSE_COMMFD=3`, and extracts the passed fd with `ParseSocketControlMessage` and `ParseUnixRights`.

Control flow: The function creates a parent/child socketpair, passes one end to `fusermount3`, logs helper stdout/stderr, waits for the helper, then converts the parent socket into `*net.UnixConn`. It reads out-of-band SCM_RIGHTS data, validates that exactly one control message and one fd were received, wraps that fd as `/dev/fuse`, and returns it to `Mount`.

State and persistence behavior: Temporary socket files/fds are closed with defers. The resulting `*os.File` represents the live kernel FUSE connection. No durable filesystem data is managed here beyond the mount itself.

Dependencies and integration points: Depends on `net`, `os`, `os/exec`, `syscall`, `sync`, `mountConfig`, and shared logging helpers. It is the Linux platform implementation behind `fuse.Mount`.

Risks: Requires `fusermount3` in PATH and user permission to mount FUSE. SCM_RIGHTS parsing assumes exactly one fd. String parsing of helper errors is brittle across helper versions/locales. If `ReadMsgUnix` returns an error, the current code proceeds to parse `oob[:oobn]` without an explicit immediate error check after the read.

Test signals: `serve_test.go` covers missing mountpoint behavior. `options_test.go` validates Linux-visible FSName/subtype/default permission/read-only option behavior. `fuse_test.go` validates negotiated flags on live mounts.
