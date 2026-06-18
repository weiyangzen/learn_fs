# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_debug.h

Read completely: 57 lines.

Defines FUSE logging, debug, and panic macros. It includes `fuse_abi.h` and uses current process command/pid for contextual log prefixes.

In the active branch, `fuse_print` and `fuse_panic` prefix messages with function, command, and pid. `fuse_dbg` logs only when global `fuse_debug` is nonzero. `fuse_dbgipc` extracts the FUSE input header from a `struct fuse_ipc` and logs pointer, inode, operation name, request length, error, and message.

The disabled branch provides simpler logging and no-op debug output.

Important dependencies: assumes `fuse_in` and `fuse_get_ops` are available through the broader FUSE implementation.

Research notes: `fuse_dbgipc` evaluates IPC header helpers when invoked, so callers must not pass malformed or uninitialized IPC objects.
