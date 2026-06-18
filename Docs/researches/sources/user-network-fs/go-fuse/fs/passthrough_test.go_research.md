## sources/user-network-fs/go-fuse/fs/passthrough_test.go

Purpose: tests Linux kernel passthrough behavior where read/write operations bypass the Go FUSE handler after a backing file is registered.

Important APIs/types/functions: `rwRegisteringNode` embeds `LoopbackNode` and wraps `Read`/`Write` to increment counters before delegating to `FileReader`/`FileWriter`. `TestPassthrough` constructs a custom `LoopbackRoot` and verifies counters remain zero after file I/O.

Control flow: the test requires effective root/CAP_SYS_ADMIN, mounts a loopback tree, checks `server.KernelSettings().Flags64()&fuse.CAP_PASSTHROUGH`, writes and reads a file, unmounts, and asserts no Go-level read/write callbacks occurred.

State and persistence: backing data lives in a temporary loopback directory. The node records read/write counts protected by a mutex.

Dependencies and integration: integrates `fs.LoopbackNode`, `fuse.CAP_PASSTHROUGH`, and kernel passthrough registration support.

Risks and test signals: skipped when permissions or kernel capability are missing. Failing counters indicate passthrough was not used or file handle registration changed.
