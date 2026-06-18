
# sources/user-network-fs/rclone/backend/local/clone_darwin.go

## Purpose
Enables local server-side copy on macOS with cgo by using APFS clonefile-style copying.

## Important APIs, Types, And Control Flow
`Fs.Copy` validates Darwin and `--local-no-clone`, requires a local `*Object`, excludes translated symlink clones, fetches metadata if enabled, creates destination parents, optionally resolves symlink targets under `--copy-links`, calls `Clone`, writes metadata, and returns the new object. `Clone` wraps `go-darwin/apfs.CopyFile` with `COPYFILE_CLONE`.

## State And Persistence
Creates a destination file that may share blocks with the source. Metadata is also persisted if requested.

## Dependencies And Integration Points
Integrates with rclone `fs.Copier`, local `Object` metadata, and APFS copyfile APIs. Disabled by build tags except `darwin && cgo`.

## Risks And Test Signals
Risks include APFS-only semantics, cgo availability, symlink mode differences, and metadata application after clone success. Tests should cover regular-file clone, fallback error behavior, `NoClone`, `--links`, `--copy-links`, and metadata preservation.
