# sources/user-network-fs/rclone/backend/fichier/structs.go

Purpose: This file defines JSON request and response structures for the 1Fichier API endpoints used by the backend.

Important APIs and types: Request types include `FileInfoRequest`, `ListFolderRequest`, `ListFilesRequest`, `DownloadRequest`, `RemoveFolderRequest`, `RemoveFileRequest`, `MakeFolderRequest`, `MoveFileRequest`, `MoveDirRequest`, `CopyFileRequest`, and `RenameFileRequest`. Response/data types include `GenericOKResponse`, `MakeFolderResponse`, `MoveFileResponse`, `MoveDirResponse`, `CopyFileResponse`, `RenameFileResponse`, `GetUploadNodeResponse`, `GetTokenResponse`, `SharedFolderResponse`, `SharedFile`, `EndFileUploadResponse`, `File`, `FilesList`, `Folder`, `FoldersList`, and `AccountInfo`.

Control flow: There is no executable flow in this file; the structures are marshaled and unmarshaled by `rest.CallJSON` in `api.go` and consumed by higher-level methods in `fichier.go` and `object.go`.

State and persistence behavior: The structs model provider state such as folder IDs, file URLs, checksums, quota counters, upload links, and account storage values. They do not maintain local state.

Dependencies and integration points: The JSON tags are the contract between the backend and 1Fichier's endpoints. `File` drives object metadata, `FoldersList` drives directory caching, `EndFileUploadResponse` drives post-upload object creation, and `AccountInfo` drives `About`.

Risks: Several 1Fichier JSON fields use inconsistent capitalization such as `Status` and `Message`; tag drift would silently break behavior. Some response slices are assumed non-empty by callers. Large `AccountInfo` coverage is broad but not validated locally.

Test signals: There are no direct tests for the DTOs; integration coverage validates only fields touched by standard operations.
