<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_linux_test.go -->
# sources/user-network-fs/bazil-fuse/fs/serve_linux_test.go

Purpose: Linux-specific adapters and OFD lock helper registration for fs package tests.

Important APIs, types, and functions: defines `platformStatfs`, `platformStat`, and registers `lock-ofd` with `lockHelp` using `unix.FcntlFlock` and OFD lock commands.

Control flow: stat helpers normalize Linux syscall structs. The init function assigns `lockOFDHelper` so shared lock tests can spawn a subprocess that sets, waits on, unlocks, and queries OFD locks.

State and persistence behavior: read-only stat conversion plus subprocess-driven kernel lock state during tests.

Dependencies and integration points: depends on Linux `golang.org/x/sys/unix`, shared fs tests, and spawntest helper infrastructure.

Risks and test signals: OFD locks are Linux-specific and require correct command selection for wait vs non-wait paths. Tests should observe lock conflicts and unlock behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_linux_test.go -->
