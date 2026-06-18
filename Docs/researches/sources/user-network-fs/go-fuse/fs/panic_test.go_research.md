## sources/user-network-fs/go-fuse/fs/panic_test.go

Purpose: verifies that panics inside high-level FS handlers are caught, logged, and translated to a kernel-visible error.

Important APIs/types/functions: `panicNode` embeds `Inode` and implements `NodeSymlinker`. Its `Symlink` method panics. `TestPanic` mounts a raw `NewNodeFS` with a logger buffer, performs `syscall.Symlink`, and checks for `EIO` plus a panic log line.

Control flow: the test bypasses `fs.Mount` to inject `MountOptions.Logger`, starts `fuse.Server`, triggers the symlink path, unmounts, and inspects the captured log.

State and persistence: transient mount and log buffer only. No durable inode changes should survive because the operation panics before returning a child.

Dependencies and integration: covers panic recovery in the `fs` bridge and `fuse.MountOptions.PanicHandler` default behavior.

Risks and test signals: prevents panics from killing the server goroutine silently or hanging kernel callers. It also verifies the log text stays useful for diagnosis.
