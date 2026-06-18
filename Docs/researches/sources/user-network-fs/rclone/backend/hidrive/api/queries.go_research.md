
# sources/user-network-fs/rclone/backend/hidrive/api/queries.go

## Purpose
This file provides query-parameter helpers and field presets for the HiDrive REST API. It centralizes path, directory/file, timestamp, list, and field selection parameter construction.

## Important APIs, Types, And Control Flow
Field presets include `HiDriveObjectNoMetadataFields`, `HiDriveObjectWithMetadataFields`, `HiDriveObjectWithDirectoryMetadataFields`, and `DirectoryContentFields`. `QueryParameters` embeds `url.Values`. `SetFileInDirectory` splits a file path into `dir` and `name` for create-style calls. `SetPath` sets the API `path` parameter. `SetTime` marshals `api.Time` as Unix seconds. `AddList` appends separator-joined values to an existing parameter, and `AddFields` prefixes field names before appending them to `fields`.

## State And Persistence
There is no persistent state. The helpers mutate in-memory `url.Values` used by REST calls.

## Dependencies And Integration Points
The helpers are used throughout `helpers.go` and `hidrive.go` for `/meta`, `/dir`, `/file`, copy/move, upload, truncate, and delete operations. They depend on `path.Clean`, `path.Split`, JSON marshaling, and URL query encoding.

## Risks And Test Signals
`SetFileInDirectory` cleans the directory component and can turn empty or relative paths into normalized values; endpoint semantics should be verified for root files. `AddList` overwrites then prepends old values, so ordering is old values first. Timestamp parameters include JSON number text, not RFC3339. Unit tests should validate query strings for root paths, nested file creation, multiple field additions, and timestamp encoding.
