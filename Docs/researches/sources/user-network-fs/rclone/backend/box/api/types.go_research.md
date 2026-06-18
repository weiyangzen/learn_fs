# sources/user-network-fs/rclone/backend/box/api/types.go

## Purpose
Defines Box API JSON request, response, event, JWT config, and error types used by the Box backend.

## Important APIs, types, and functions
`Time` marshals/unmarshals Box RFC3339 timestamps. `Error` models Box error responses and implements `error`. `ItemFields`, item type/status constants, `ItemMini`, `Item`, and `FolderItems` model files, folders, listings, upload results, owners, shared links, and timestamps. `Item.ModTime` prefers content modification time and falls back to modified time. Request/response types cover folder creation, upload/pre-upload checks, metadata updates, move/copy, shared links, multipart upload sessions/parts/commit, JWT app config, user quota, and change events.

## Control flow
Runtime logic is minimal: time JSON conversion, error string formatting, and modtime selection. Struct tags drive all Box REST serialization/deserialization.

## State and persistence
Represents remote Box state for files, folders, upload sessions, parts, shared links, users, app credentials, and events. It does not persist local state.

## Dependencies and integration points
Imported by `box.go` and `upload.go`. Depends only on Go JSON/time/fmt packages. Schema compatibility is critical for folder listing, pre-upload conflict handling, JWT auth, multipart upload, trash cleanup, quota, and event polling.

## Risks
`Item.Size` is `float64` because Box can return exponent notation, which risks precision loss when converted to `int64`. `FolderItems.Order` is commented out due to inconsistent Box shapes. Event filtering depends on `FileTreeChangeEventTypes` staying current. `Time` accepts only RFC3339.

## Test signals
No direct tests in this set; exercised indirectly by Box integration operations, uploads, quota, pre-upload checks, multipart commit, and event parsing.
