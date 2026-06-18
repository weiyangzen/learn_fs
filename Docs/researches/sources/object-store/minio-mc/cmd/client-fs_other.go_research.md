# sources/object-store/minio-mc/cmd/client-fs_other.go

## Purpose

This build-tagged file covers Solaris and OpenBSD filesystem behavior where mc supports basic notify event classification but does not expose xattr preservation.

## Important APIs, Control Flow, And State

The file defines put events as create/write/rename, delete as remove, and no get events. `IsGetEvent` returns false, `IsPutEvent` scans for bit overlap, and `IsDeleteEvent` checks remove. `getAllXattrs` returns nil metadata and nil error, making preserve-mode callers degrade gracefully on these platforms.

## Dependencies, Integration, Risks, And Tests

Only `notify` is imported. The implementation is consumed by `fsClient.Watch`, `Get`, and `Stat`. There is no persistence in this file. Risks are expected feature gaps: no get notifications and no xattr reporting, which can surprise users relying on preserve mode across platforms. Coverage is mostly by successful platform builds and shared filesystem tests.
