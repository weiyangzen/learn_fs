
# sources/user-network-fs/rclone/backend/hidrive/api/types.go

## Purpose
This file defines HiDrive API value types, error decoding structures, object metadata, and directory listing response shapes.

## Important APIs, Types, And Control Flow
`Time` marshals and unmarshals API timestamps as Unix seconds. `Error` implements `error` and preserves numeric code, message, and raw context. `HiDriveObject` models files, directories, and symlinks with IDs, names, paths, size, member count, times, hash fields, permissions, and MIME type. `HiDriveObject.ModTime` falls back from `mtime` to `ctime`. `UnmarshalJSON` sets default `Size` and `MemberCount` to `-1` and path-unescapes names. `DirectoryContent` defaults `TotalCount` to `-1`.

## State And Persistence
These are data transfer objects only. Defaults affect in-memory behavior when API fields are omitted.

## Dependencies And Integration Points
`hidrive.go` uses `HiDriveObject` to populate rclone objects and dirs. `helpers.go` uses `Error` through `isHTTPError` and `DirectoryContent` for pagination. The custom time representation is shared with query timestamp setters.

## Risks And Test Signals
Defaulting missing sizes/member counts to `-1` is important for distinguishing unknown values from zero. Path-unescaping names can hide malformed escapes by leaving the original on error. `Error.Code` is a `json.Number`, so callers must handle non-numeric codes. Tests should cover timestamp round trips, omitted fields, escaped names, directory content defaults, and `Error.Error` formatting with and without context.
