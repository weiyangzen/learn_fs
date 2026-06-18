# sources/user-network-fs/bazil-fuse/mount_freebsd.go

Purpose: This file implements the FreeBSD FUSE mount operation using `/dev/fuse` and `/sbin/mount_fusefs`.

Important APIs, types, and functions: `handleMountFusefsStderr` parses mount helper stderr and turns missing mountpoint messages into `MountpointDoesNotExistError`. `isBoringMountFusefsError` suppresses uninteresting exit status 1 when a better parsed error exists. `mount(dir, conf)` validates options, opens `/dev/fuse`, and runs `mount_fusefs --safe -o <opts> 3 <dir>` with the FUSE fd passed as an extra file.

Control flow: Before mounting, it rejects option keys or values containing commas because FreeBSD's helper does not support escaping. It opens `/dev/fuse`, configures command pipes and `ExtraFiles`, starts stdout/stderr loggers, waits for helper output to drain, then waits for process exit. If stderr produced a structured missing-mountpoint error, that error is returned in preference to the generic exit error.

State and persistence behavior: The live mount and `/dev/fuse` file descriptor are the only state. No repository state is written.

Dependencies and integration points: Depends on `os`, `os/exec`, `syscall`, `strings`, `sync`, logging helpers from `mount.go`, and `mountConfig.getOptions`. It is called by `Mount` in `fuse.go` on FreeBSD.

Risks: Option comma rejection is platform-specific and can surprise callers. The code assumes `/dev/fuse` and `/sbin/mount_fusefs` are available and that fd `3` is accepted by the helper. Helper output parsing is string-fragile.

Test signals: `serve_test.go` validates missing mountpoint error typing. `options_test.go` skips unsupported FSName/subtype/default permission behavior on FreeBSD and notes several FreeBSD kernel/helper differences.
