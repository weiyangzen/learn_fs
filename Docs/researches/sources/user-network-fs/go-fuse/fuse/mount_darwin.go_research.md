## sources/user-network-fs/go-fuse/fuse/mount_darwin.go

Purpose: macOS mount and unmount implementation using macFUSE/osxfuse helper binaries.

Important APIs/types/functions: `getMaxWrite` returns 1 MiB. `unixgramSocketpair` creates a socketpair. `mount` invokes `mount_macfuse`/`mount_osxfuse` with environment variables and fd 3 communication, receives the FUSE fd, and reports helper completion on `ready`. `unmount` calls `syscall.Unmount`. `fusermountBinary` locates helper paths.

Control flow: create socketpair, start helper with remote socket as extra file, receive fd with `getConnection`, set close-on-exec, and asynchronously wait for helper after server startup.

State and persistence: mount state is kernel state plus helper process lifecycle; no Go persistent data beyond fd ownership.

Dependencies and integration: plugs into `fuse.NewServer` on Darwin.

Risks and test signals: helper path, fd inheritance, and delayed helper wait are fragile. Failures appear as mount timeouts or missing FUSE fd on macOS.
