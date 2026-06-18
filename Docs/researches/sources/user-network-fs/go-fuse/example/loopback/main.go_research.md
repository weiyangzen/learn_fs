# sources/user-network-fs/go-fuse/example/loopback/main.go

Purpose: command-line loopback filesystem that mirrors operations to a backing directory.

Important functions/options: `writeMemProfile` writes heap profiles on SIGUSR1; `main` parses debug, allow-other, idmapped, quiet, read-only, direct mount, CPU/memory profile flags; creates `fs.NewLoopbackRoot`; configures attr/entry one-second TTLs, `NullPermissions`, FUSE mount names, allow_other/default_permissions, read-only mount option, and logger; mounts and waits while handling SIGINT/SIGTERM for unmount.

State/dependencies: persistent state is the backing filesystem. Profiles are written to requested files.

Integration/risks: relies on `fs.LoopbackNode` syscall passthrough and kernel FUSE options. Risks include allow_other requiring fuse.conf, profiles needing graceful unmount, and backing mutations being real. Test signal comes from loopback tests and manual use.
