<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/drive.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/drive.go

### Purpose
`drive.go` implements iCloud Drive API operations as a `DriveService`. It wraps Apple's drivews and docws endpoints for item lookup, folder listing, download URL resolution, uploads, file updates, folder creation, move, rename, trash, and type conversion between several Apple response shapes.

### Important APIs, Types, and Functions
`DriveService` stores the owning `Client`, root drive ID, drive endpoint, and docs endpoint. Lookup methods include `GetItemByDriveID`, `GetItemsByDriveID`, `GetDocByPath`, `GetItemByPath`, `GetDocByItemID`, `GetItemRawByItemID`, and `GetItemsInFolder`. Mutation methods include `MoveItemToTrashByItemID`, `MoveItemToTrashByID`, `CreateNewFolderByItemID`, `CreateNewFolderByDriveID`, `RenameItemByItemID`, `RenameItemByDriveID`, `MoveItemByItemID`, `MoveItemByDriveID`, `CopyDocByItemID`, `CreateUpload`, `Upload`, and `UpdateFile`.

Important models are `UpdateFileInfo`, `FileFlags`, `DriveItemRaw`, `DriveItemRawInfo`, `DocumentUpdateResponse`, `Document`, `DocumentData`, `SingleFileResponse`, `UploadResponse`, `FileRequest`, `CreateFoldersResponse`, and `DriveItem`. Helpers include `NewUpdateFileInfo`, `DriveItemRaw.SplitName`, `ModTime`, `CreatedTime`, `IntoDriveItem`, `Document.DriveID`, `DriveItem.IsFolder`, `DownloadURL`, `FullName`, `GetDocIDFromDriveID`, `DeconstructDriveID`, `ConstructDriveID`, and `GetContentTypeForFile`.

### Control Flow
Most methods construct JSON payloads with `IntoReader`, set session headers via `Session.GetHeaders`, select either drivews or docws, then call `Client.Request` for auth-aware retry. Item-ID methods often first resolve a document to a drivews ID, because mutation endpoints operate on drivews IDs. Rename, move, and trash operations inspect per-item status and, when `force` is true and Apple reports `ETAG_CONFLICT`, retry once using the latest returned etag.

Downloads first resolve a `FileRequest` to either `DataToken.URL` or `PackageToken.URL`. `DownloadFile` then performs a raw GET and recursively follows Apple's nonstandard HTTP 330 redirect if a `Location` header is available. Uploads are two-phase: `CreateUpload` requests an upload URL and document ID, `Upload` posts the file body to that URL, and `UpdateFile` commits document metadata and content receipts.

### State and Persistence
This layer does not persist local state. It consumes session cookies and webservice endpoints from `Client.Session.AccountInfo.Webservices`. It maps server timestamps into `time.Time` and constructs returned `DriveItem` values after updates. `NewUpdateFileInfo` sets default update flags (`add_file`, conflict allowed, writable/executable visible file flags).

### Dependencies and Integration Points
The service depends on `Client.Request`, `Session.GetHeaders`, rclone `rest` and `fs.OpenOption`, standard `mime`, `url`, `uuid`, and time parsing. Higher-level backend code uses these methods to implement rclone filesystem operations. The `defaultZone` constant anchors CloudDocs document operations unless a drive ID includes a different zone.

### Risks and Edge Cases
Several methods assume non-empty server arrays and access `[0]` without length checks, so malformed or empty Apple responses can panic. `NewDriveService` assumes both drive and docs webservice entries exist. `SplitName` relies on filename text because Apple extension fields are noted as unreliable. MIME detection falls back to `text/plain`, which satisfies API requirements but may be semantically weak for unknown binary files. Etag force retries are limited and should not mask persistent conflicts.

### Test Signals
No direct drive API unit test appears in this subset. Huawei tests cover a similar MIME fallback concept, but this file is mainly validated by higher-level iCloud Drive backend tests outside the listed files and by live integration behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/drive.go -->
