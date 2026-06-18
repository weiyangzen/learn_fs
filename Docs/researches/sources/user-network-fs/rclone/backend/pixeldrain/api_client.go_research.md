# sources/user-network-fs/rclone/backend/pixeldrain/api_client.go

Purpose: low-level PixelDrain filesystem API wrapper for the rclone backend. It defines API models, error normalization, retry handling, metadata parameter mapping, path escaping, and REST helpers.

Important APIs/types/functions: models include `FilesystemPath`, `FilesystemNode`, `ChangeLog`, `ChangeLogEntry`, `UserInfo`, `SubscriptionType`, and `APIError`. Error sentinels are `errNotFound`, `errExists`, and `errAuthenticationFailed`. `apiErrorHandler` maps PixelDrain status values to rclone errors. `paramsFromMetadata`, `nodeToObject`, `nodeToDirectory`, and `escapePath` adapt paths and metadata. Helpers include `put`, `read`, `stat`, `changeLog`, `update`, `mkdir`, `rename`, `delete`, and `userInfo`.

Control flow: errors are decoded from JSON and response bodies are closed on error. Paths are prefixed with the backend root and URL-escaped segment by segment. `stat` uses `?stat` to force metadata responses for files. `put` sets `make_parents=true`; `update`/`rename` use action multipart params; `delete` can pass `recursive=true`. `rename` verifies compatible PixelDrain source FS and same root folder ID.

State and persistence: no local independent state. Functions mutate remote nodes, metadata, sharing/logging flags, and expose change logs. Metadata keys include mtime, btime, mode, shared, and logging_enabled.

Dependencies/integration: uses rclone `fs`, `fserrors`, `rest`, and standard HTTP/URL/JSON packages. High-level methods in `pixeldrain.go` call these helpers.

Risks/test signals: `FilesystemPath.Base` trusts API `BaseIndex`. `APIError.Error` returns only status code, losing message context. Change logs require remote logging and have retention constraints. Integration tests exercise this wrapper indirectly.
