# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unsupported.go

## Purpose
Provides xattr stubs for platforms without supported extended attribute implementation.

## Important APIs, Types, and Functions
`GetXattr` and `SetXattr` both return `ErrXattrsNotSupported`.

## Control Flow
No filesystem access is attempted.

## State and Persistence Behavior
No state or mutation.

## Dependencies and Integration Points
Builds for Windows, DragonFly, illumos, Solaris, and OpenBSD. Satisfies the `Filesystem` interface and lets callers detect unsupported xattrs via `errors.Is`.

## Risks
Callers must treat unsupported xattrs as a capability gap, not a hard sync failure unless configured to require them.

## Test Signals
`TestXattr` skips when `ErrXattrsNotSupported` is returned.
