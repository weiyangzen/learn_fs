# sources/user-network-fs/bazil-fuse/fuse_test.go

Purpose: This integration test validates feature flag negotiation between mount options and the FUSE kernel during `Mount`.

Important APIs, types, and functions: `getFeatures` mounts a temporary filesystem and returns `Conn.Features()`. `TestFeatures` checks `LockingFlock`, `LockingPOSIX`, `AsyncRead`, `WritebackCache`, `CacheSymlinks`, and `ExplicitInvalidateData` mount options against negotiated `InitFlags`.

Control flow: For each subtest, the test mounts an empty temporary FUSE filesystem with selected options, reads negotiated flags, computes missing wanted bits and disallowed extra bits, and unmounts/cleans up. FreeBSD skips `InitFlockLocks` expectations because FreeBSD FUSE does not implement flock locks.

State and persistence behavior: Uses a temporary directory and a live kernel mount; all state is cleaned up through `conn.Close`, `fuse.Unmount`, and `os.RemoveAll`.

Dependencies and integration points: Depends on working FUSE mount support, platform mount helpers, and the public `fuse` API. It directly validates the `Mount` -> `initMount` -> `Conn.Features` path.

Risks: Environment-sensitive and may fail without FUSE privileges or helper binaries. It does not validate max background/congestion values or every feature bit.

Test signals: Strong signal that option-selected `InitFlags` survive negotiation and that default bare mounts do not unexpectedly enable POSIX/flock locking.
