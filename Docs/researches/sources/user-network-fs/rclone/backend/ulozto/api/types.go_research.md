# sources/user-network-fs/rclone/backend/ulozto/api/types.go

Purpose: JSON contract definitions for the Uloz.to backend. `ulozto.go` uses these for auth, listing, folder/file mutation, upload session management, download links, and API error handling.

Important APIs/types: `Error` implements `error` and broad `Is` matching. Data types include `Folder`, `File`, `ListFoldersResponse`, `ListFilesResponse`, `FolderSizesResponse`, upload/session structs, move/rename/update request structs, and `AuthenticateRequest`/`AuthenticateResponse`.

Control flow/state: no persistent state or network calls. The only behavior is error formatting/matching; all other state is transient JSON decoded by `rest.CallJSON`.

Dependencies/integration: standard `errors`, `fmt`, `time`; integrated by exact JSON tags with Uloz.to `/v5` through `/v9` endpoints.

Risks/test signals: schema drift and permissive `Error.Is` matching are main risks. No direct unit tests; live Uloz.to integration and compile-time backend usage are the signals.
