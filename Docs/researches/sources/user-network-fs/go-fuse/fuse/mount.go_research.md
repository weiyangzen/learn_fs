## sources/user-network-fs/go-fuse/fuse/mount.go

Purpose: shared mount plumbing for inherited FUSE file descriptors and fd reservation.

Important APIs/types/functions: package-level `reservedFDs` holds pipes to keep fd 3 from accidentally becoming a FUSE fd. `init` reserves low fds. `getConnection(local *os.File)` reads an fd sent over a Unix socket using `ReadMsgUnix` and `SCM_RIGHTS`.

Control flow: OS-specific mount helpers create socket pairs and privileged helper processes; `getConnection` receives the opened `/dev/fuse` fd from the helper.

State and persistence: `reservedFDs` intentionally leaks low-numbered descriptors for process lifetime to avoid helper deadlocks.

Dependencies and integration: used by Darwin/Linux mount helpers and mount tests.

Risks and test signals: fd handling is delicate. Incorrect reservation or control-message parsing can deadlock mounting or receive the wrong fd.
