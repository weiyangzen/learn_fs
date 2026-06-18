<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/debug.go -->
# sources/user-network-fs/bazil-fuse/debug.go

Purpose: package-level debug hook for FUSE protocol and server trace messages.

Important APIs, types, and functions: `stack` captures the current goroutine stack, `nop` discards messages, and exported variable `Debug func(msg interface{})` defaults to `nop`.

Control flow: other package code calls `fuse.Debug` with JSON-safe, human-readable values; callers may replace it before serving.

State and persistence behavior: global process state is the `Debug` function pointer; no persistent storage.

Dependencies and integration points: used by the FUSE connection and `fs.Server` debug plumbing; test utilities can redirect it to logs.

Risks and test signals: implementations must not retain `msg`. Racy global replacement can affect concurrent connections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/debug.go -->
