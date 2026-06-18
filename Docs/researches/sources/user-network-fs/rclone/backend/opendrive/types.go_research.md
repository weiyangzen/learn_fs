# sources/user-network-fs/rclone/backend/opendrive/types.go

Purpose: defines JSON request and response DTOs for OpenDrive API calls and the backend-specific error type.

Important APIs and types: `Error` wraps OpenDrive `error.code` and `error.message` and implements `Error()`. `Account` is the login request. `UserSessionInfo` models login/session response fields used primarily for `SessionID`, while preserving many returned account fields. `FolderList`, `Folder`, and `File` model listing and file metadata. Request/response structs include `createFolder`, `createFolderResponse`, `moveCopyFolder`, `renameFolder`, `moveCopyFolderResponse`, `removeFolder`, `moveCopyFile`, `moveCopyFileResponse`, `renameFile`, `createFile`, `createFileResponse`, `modTimeFile`, `openUpload`, `openUploadResponse`, `closeUpload`, `closeUploadResponse`, `permissions`, `uploadFileChunkReply`, and `usersInfoResponse`.

Control flow integration: `opendrive.go` serializes these structs through `rest.CallJSON`. Login sends `Account` and receives `UserSessionInfo`. Listing decodes `FolderList` into folders and files. Upload flow creates a file, opens upload, uploads chunks, closes upload, sets permissions, and refreshes metadata using this file's DTOs. Copy/move and rename paths switch between move/copy and rename request structs depending on parent directory.

State and persistence behavior: these structs are transient JSON carriers for persistent OpenDrive remote state. Several numeric values are encoded as JSON strings, such as `File.Size`, `File.DateModified`, `usersInfoResponse.StorageUsed`, and `MaxStorage`; the tags are critical for correct decoding.

Dependencies and integration points: only imports `encoding/json` and `fmt`. `json.RawMessage` is used for `IsAccountUser` because the API may return inconsistent shapes.

Risks: field names mirror OpenDrive's mixed casing exactly, so tag drift can break behavior silently. Some response fields represent numbers as strings while similar fields use integers, which can cause parse or zero-value issues. Many structs include fields not actively used by the backend; they may become stale relative to API behavior. Error responses without message/code are normalized by `errorHandler` in `opendrive.go`.

Test signals: no direct tests target these DTOs. They are indirectly covered by live `opendrive_test.go` integration behavior and by any operations that decode corresponding API responses.
