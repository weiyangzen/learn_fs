# sources/user-network-fs/rclone/backend/sharefile/api/types.go

Purpose: DTO and error types for the ShareFile backend API.

Important APIs/types/functions: `ListRequestSelect` defines the OData projection for child listing. `ListResponse` wraps `odata.count` and `[]Item`. `Item` models files/folders with names, dates, hidden flag, size, OData type, ID, and hash. `Error` implements Go's `error` interface for OData error responses. `DownloadSpecification`, `UploadRequest`, `UploadSpecification`, and `UploadFinishResponse` model download and upload negotiation/completion. `UploadFinishResponse.ID` returns the first uploaded item ID or a clear error. `Parent`, `Zone`, and `UpdateItemRequest` support item updates/moves.

Control flow: behavior is limited to `Error.Error` string formatting and `UploadFinishResponse.ID` validation. Other types are marshaled/unmarshaled by backend REST calls.

State and persistence behavior: no persistent state. Timestamps and IDs are transient API payloads.

Dependencies/integration: imports `time`, `fmt`, and `errors`. It is intended to be consumed by the ShareFile backend implementation for OData listing, upload, download, patch, and error handling.

Risks/test signals: risks are schema drift, OData field naming, pointer optional fields, and upload completion responses with no `Value`. No direct tests are present in this subset.
