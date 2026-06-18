# sources/user-network-fs/bazil-fuse/options_test.go

Purpose: This integration test file validates public mount options against real kernel-visible behavior.

Important APIs, types, and functions: Tests cover `FSName`, escaping of unusual FS names, `Subtype`, `AllowOther`, `DefaultPermissions`, `ReadOnly`, `MaxBackground`, and `CongestionThreshold`. Helpers include `etcFuseHasAllowOther`, `openErrHelper`, `unwritableFile`, and `createrDir`.

Control flow: Tests mount temporary FUSE filesystems with selected options, then inspect mount metadata or drive syscalls through helper subprocesses. FSName/subtype tests inspect mount info. Permission tests attempt opens/creates and check kernel-returned errnos. Max background and congestion threshold tests currently only verify mount success and contain TODOs to inspect `/sys/fs/fuse/connections`.

State and persistence behavior: Test state is temporary mountpoints and helper processes. No durable repository state is changed.

Dependencies and integration points: Depends on FUSE mounts, `/etc/fuse.conf` for `AllowOther`, `fstestutil`, `spawntest`, `httpjson`, and the `fuse/fs` server layer. FreeBSD skips unsupported options.

Risks: Environment-sensitive; tests skip or fail depending on system FUSE configuration and privileges. FSName option order is not tested because option serialization uses a map. MaxBackground/CongestionThreshold lack assertions beyond successful mount.

Test signals: Strong coverage for option escaping and security-sensitive behavior: `DefaultPermissions` should make the kernel enforce file modes, and `ReadOnly` should block creation before the filesystem's `Create` method returns its distinct error.
