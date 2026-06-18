# sources/user-network-fs/go-fuse/fs/bridge_nonlinux.go

Purpose: non-Linux fallback for `rawBridge.Statx`.

Important API: `Statx` has the same signature as Linux bridge support and always returns `fuse.ENOSYS`.

Control flow/state: none beyond immediate status return.

Dependencies/integration: build-tagged `!linux`; ensures the fs package compiles on platforms without Linux statx support. Risks are minimal; platform consumers must tolerate statx absence and fall back to getattr. Cross-builds in `all.bash` for Darwin and FreeBSD are the main test signal.
