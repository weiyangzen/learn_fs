## sources/user-network-fs/go-fuse/fuse/mount_linux.go

Purpose: Linux mount/unmount implementation supporting direct `mount(2)`, fusermount helper, `/dev/fd/N` inherited mounts, option assembly, and max-write limits.

Important APIs/types/functions: `unixgramSocketpair`, `mountDirect`, `callFusermount`, `mount`, `unmount`, `lookPathFallback`, `fusermountBinary`, `umountBinary`, `getMaxWrite`, and `maxPageLimit`.

Control flow: `mount` handles `/dev/fd/N`, strict/direct mount, or fusermount fallback. Direct mount opens `/dev/fuse`, builds `fd=`, rootmode, user/group, max_read, and option strings, then calls `syscall.Mount`. Fusermount starts helper, receives fd over socket, and waits asynchronously. `unmount` tries direct unmount or helper fallback.

State and persistence: mount state is kernel-managed; Go owns the `/dev/fuse` fd and helper process state. Mount options encode persistent kernel behavior for the mount lifetime.

Dependencies and integration: central Linux backend for all FUSE server tests, including direct mount, idmapped mount, and max write negotiation.

Risks and test signals: option escaping, fd passing, privilege fallback, and max page detection are high-risk. `mount_linux_test.go` covers major branches.
