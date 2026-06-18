# sources/object-store/minio-mc/cmd/client-fs_netbsd.go

## Purpose

This NetBSD companion supplies the filesystem backend's platform-specific event classification and xattr readers. Its behavior matches the BSD-style pattern used by the Darwin and FreeBSD files.

## Important APIs, Control Flow, And State

Put events are create/write/rename, delete events are remove, and get events are unsupported. `IsGetEvent` returns false, `IsPutEvent` tests the configured event set, and `IsDeleteEvent` checks `notify.Remove`. `getXAttr` and `getAllXattrs` fetch all xattrs into a string map, treating unsupported xattrs as a nil metadata result.

## Dependencies, Integration, Risks, And Tests

Dependencies are `notify` and `xattr`; consumers are the shared filesystem client's watch and preserve paths. The file does not persist state itself. Risks are missing access events and xattr races between list and read. Test signals come from successful NetBSD compilation plus shared filesystem behavior tests.
