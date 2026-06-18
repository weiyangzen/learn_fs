# sources/user-network-fs/rclone/backend/fichier/api.go

Purpose: This file contains the low-level 1Fichier API helpers used by the backend: retry classification, file/folder listing, shared-folder access, folder mutations, file move/copy/rename/delete, upload-node discovery, multipart form upload, and upload finalization.

Important APIs and types: Important functions include `parseFichierError`, `shouldRetry`, `createObject`, `readFileInfo`, `getDownloadToken`, `listSharedFiles`, `listFiles`, `listFolders`, `listDir`, `newObjectFromFile`, `makeFolder`, `removeFolder`, `deleteFile`, `moveFile`, `moveDir`, `copyFile`, `renameFile`, `getUploadNode`, `uploadFile`, and `endUpload`. It uses request/response DTOs from `structs.go`, `rest.Opts`, `dircache`, and rclone `fs.DirEntry`/`fs.Dir`.

Control flow: API calls are wrapped in `f.pacer.Call` or `CallNoRetry` with JSON requests to the 1Fichier API. Listing resolves a directory ID from `dirCache`, fetches files and folders separately, converts server names through the configured encoder, emits objects/directories, and stores folder IDs back into `dirCache`. Uploads first obtain an upload node, POST the file as multipart form data to `/upload.cgi` with an upload ID, then call `/end.pl` on that node to retrieve final links. Shared folder listing switches between GET and POST depending on password presence.

State and persistence behavior: The file maintains no persistent local state, but it updates `dirCache` when listing folders and creates/deletes/moves/copies server-side 1Fichier objects. Upload state is provider-side and keyed by upload node ID. `shouldRetry` may sleep for 30 seconds for parsed flood errors `#374` or `#412`.

Dependencies and integration points: It integrates with `lib/rest`, `fs.Pacer`, `fserrors`, `dircache.DirCache`, 1Fichier's JSON endpoints, and encoding conversion. Higher-level `fichier.go` operations call these helpers to implement rclone interfaces, while `object.go` calls `getDownloadToken` and `deleteFile`.

Risks: 1Fichier overloads HTTP 403 for many API failures, so parsing numeric codes out of error strings is fragile. The flood-control sleep blocks the pacer caller. Upload IDs are validated only for alphanumeric length, and upload finalization assumes at least one returned link. Listing and dates depend on exact server time formats. Shared-folder response handling has limited password and error coverage.

Test signals: There are no direct unit tests for these helpers; the `fichier` integration test exercises them through standard filesystem operations against `TestFichier:`.
