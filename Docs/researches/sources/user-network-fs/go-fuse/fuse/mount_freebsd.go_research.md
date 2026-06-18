## sources/user-network-fs/go-fuse/fuse/mount_freebsd.go

Purpose: FreeBSD mount and unmount implementation using `mount_fusefs`.

Important APIs/types/functions: `getMaxWrite`, `callMountFuseFs`, `mount`, `unmount`, and `fusermountBinary`. The code opens `/dev/fuse`, forks `mount_fusefs --safe`, passes fd 3, waits for helper status, and returns the device fd.

Control flow: direct raw fd management avoids Go GC closing descriptors. Errors close fds through deferred cleanup. `mount` coordinates helper completion with server readiness.

State and persistence: kernel mount and `/dev/fuse` fd are the primary state; file descriptors must remain open for mount lifetime.

Dependencies and integration: FreeBSD-specific backend for `fuse.NewServer`.

Risks and test signals: fd lifetime and helper exit interpretation are key risks. FreeBSD CI/mount tests are needed for coverage.
