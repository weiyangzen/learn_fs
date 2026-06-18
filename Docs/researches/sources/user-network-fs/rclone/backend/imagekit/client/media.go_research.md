# sources/user-network-fs/rclone/backend/imagekit/client/media.go

## Purpose
Implements ImageKit media-library file and folder API calls plus the response/parameter models used by the backend.

## Important APIs, Types, and Functions
Models include `FilesOrFolderParam`, `AITag`, `File`, `Folder`, folder operation params, `JobIDResponse`, and `JobStatus`. Methods include `File`, `Files`, `DeleteFile`, `Folders`, `CreateFolder`, `DeleteFolder`, `MoveFolder`, and `BulkJobStatus`.

## Control Flow
`Files` and `Folders` call `GET /files` with `skip`, `limit`, `path`, and `searchQuery`, defaulting to file or folder type filters. `Files` can include file versions by changing the search query. Folder create/delete validate nonzero fields with `validator.v2` before JSON requests. `MoveFolder` starts a bulk move job; `BulkJobStatus` fetches job state.

## State and Persistence
The methods do not cache state. They marshal request params and unmarshal ImageKit API responses into Go structs. Deletion and folder moves mutate remote ImageKit media-library state.

## Dependencies and Integration Points
Uses `lib/rest`, `net/url`, `validator.v2`, and ImageKit's REST endpoints under `ImageKit.Prefix`. Backend helpers in `util.go` page through `Files`/`Folders` and perform name lookups with search queries.

## Risks and Edge Cases
`File.Width` and `UploadResult.Width` use JSON tag `"Width"` with uppercase W, matching existing code but potentially surprising if ImageKit returns lowercase `width`. `File` calls ignore status to allow callers to inspect response status, while most other methods rely on rest error behavior. Search query strings are caller-built and must quote names correctly.

## Test Signals
No local unit tests target this client. Coverage comes from ImageKit integration tests and backend list/object operations.
