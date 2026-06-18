# sources/user-network-fs/rclone/backend/filelu/filelu_client.go

Purpose: This file contains FileLu API client helpers for multipart initialization/completion, folder CRUD/listing, direct download links, file delete, account info, and file info.

Important APIs and types: Functions include `multipartInit`, `completeMultipart`, `createFolder`, `getFolderList`, `deleteFolder`, `getDirectLink`, `deleteFile`, `getAccountInfo`, and `getFileInfo`. It uses DTOs from `backend/filelu/api`, `rest.Opts`, the backend HTTP client, and FileLu key authentication on query parameters.

Control flow: Most helpers issue GET requests through `f.srv.CallJSON` inside the pacer and check `Status == 200`. `completeMultipart` uses a raw POST to the upload server with `X-RC-Upload-Id`, `X-Sess-ID`, and `X-Object-Path` headers and expects HTTP 202. `getFolderList` converts remote folder paths and file names back to standard encoding. `getFileInfo` returns `fs.ErrorObjectNotFound` if status is not 200 or the result list is empty.

State and persistence behavior: The helpers do not store local state; they create, list, and delete provider state. Multipart upload state is represented by upload ID, session ID, server, and object path supplied by the provider.

Dependencies and integration points: Higher-level methods in `filelu.go`, `filelu_file_uploader.go`, and `filelu_object.go` call these helpers. They integrate with rclone retry classification through `shouldRetry`, `shouldRetryHTTP`, and `fserrors.ShouldRetry`.

Risks: API keys are sent as query parameters. Retry handling sometimes wraps errors before returning retry decisions. Completion reads and returns response bodies only on non-202. Folder-not-found detection is string based. There is limited validation of returned server URLs and multipart IDs.

Test signals: There are no direct unit tests; the generic FileLu integration suite indirectly exercises folder, upload, download, and delete helpers.
