## sources/user-network-fs/go-fuse/fuse/passthrough_linux.go

Purpose: Linux support for registering kernel passthrough backing file descriptors.

Important APIs/types/functions: ioctl constants `_DEV_IOC_BACKING_OPEN` and `_DEV_IOC_BACKING_CLOSE`; `Server.RegisterBackingFd(*BackingMap)` and `Server.UnregisterBackingFd(id int32)`.

Control flow: methods serialize ioctl calls with `writeMu`, call `SYS_IOCTL` on the mount fd, log when debug is enabled, and return kernel id/errno.

State and persistence: kernel stores backing fd registrations until unregistered or mount teardown. Server mutex protects mount fd writes.

Dependencies and integration: used by high-level loopback passthrough support and tested by `fs/passthrough_test.go`.

Risks and test signals: registration lifecycle leaks or inconsistent ids can bypass wrong files. Requires kernel capability and elevated privileges in tests.
