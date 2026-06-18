# sources/sync-backup/syncthing/lib/fs/basicfs_watch_unsupported.go

## Purpose
Provides a `BasicFilesystem.Watch` implementation for build targets where recursive watching is intentionally unsupported.

## Important APIs, Types, and Functions
`Watch(name string, ignore Matcher, ctx context.Context, ignorePerms bool)` returns nil channels and `ErrWatchNotSupported`.

## Control Flow
No setup is attempted on unsupported builds.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Selected for Solaris without cgo, Darwin without cgo, Android amd64, or Darwin kqueue builds. Satisfies the `Filesystem` interface.

## Risks
Callers must handle `ErrWatchNotSupported` and fall back to periodic scanning. Build tags must stay aligned with event mask files.

## Test Signals
Unsupported behavior is compile-time/platform-gated rather than directly tested in this subset.
