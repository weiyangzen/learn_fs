# sources/user-network-fs/rclone/backend/filelu/api/types.go

Purpose: This package defines response structures for FileLu API calls used by the backend.

Important APIs and types: The DTOs include `MultipartInitResponse`, `CreateFolderResponse`, `DeleteFolderResponse`, `FolderListResponse`, `FileDirectLinkResponse`, `FileInfoResponse`, `DeleteFileResponse`, and `AccountInfoResponse`. Nested anonymous structs model upload IDs, session IDs, upload server, folder IDs, object paths, file codes, paths, sizes, hashes, and account storage strings.

Control flow: There is no executable logic; `filelu_client.go`, `filelu_file_uploader.go`, and `filelu_object.go` unmarshal these responses from `rest.CallJSON` or manual HTTP calls.

State and persistence behavior: The structs represent remote folder/file metadata, upload session state, direct links, deletion status, and quota fields. They do not store local state.

Dependencies and integration points: The file depends only on `encoding/json` for `json.Number`. It is the schema contract for FileLu list, upload, delete, account, and file-info operations.

Risks: The backend assumes status `200` means success and often trusts nested fields. Storage values are strings parsed elsewhere as GB. Several nested response shapes are anonymous, which reduces reuse and makes schema drift harder to test directly.

Test signals: No direct DTO tests exist; generic FileLu integration tests indirectly cover the fields used by standard operations.
