# sources/user-network-fs/rclone/backend/onedrive/metadata.go

## Purpose
`metadata.go` implements OneDrive metadata support for files and directories. It maps rclone `fs.Metadata` keys to Microsoft Graph item metadata, controls optional permission read/write behavior, creates and updates directory metadata, preserves birth/modification times, and exposes metadata/modtime methods for OneDrive objects and directories.

## Important APIs, Types, And Functions
Important definitions include `systemMetadataInfo`, `rwChoices`, `rwChoice`, `rwRead`, `rwWrite`, `rwFailOK`, `rwOff`, `rwExamples`, and the `Metadata` struct. `Metadata` caches MIME type, description, mtime, btime, upload time, creator/modifier identities, malware/package/shared flags, normalized ID, current permissions, queued permissions, and add-only permission mode.

Key methods are `Metadata.Get`, `Set`, `toAPIMetadata`, `Write`, `RefreshPermissions`, `WritePermissions`, `orderPermissions`, `sortPermissions`, `processPermissions`, `addPermission`, `updatePermission`, `removePermission`, `Fs.getPermissions`, `Fs.newMetadata`, `needsUpdatePermissions`, `Object.fetchMetadataForCreate`, `Fs.fetchAndUpdateMetadata`, `Object.updateMetadata`, `Fs.MkdirMetadata`, `createDir`, `updateDir`, `newDir`, `Object.Metadata`, `DirSetModTime`, `Directory.SetModTime`, `Directory.Metadata`, `Directory.SetMetadata`, and directory interface methods.

## Control Flow
Reading metadata is mostly local: `Get` formats cached system fields into `fs.Metadata`. If permission reading is enabled, it makes a Graph `/permissions` call, caches the result, marshals it to JSON, and includes it as the `permissions` key.

Writing begins with `Set`, which accepts writable keys. `mtime` and `btime` parse RFC3339 input into cached times; `description` is logged and skipped because Microsoft no longer supports it; `permissions` is unmarshaled only when permission write is enabled. `toAPIMetadata` builds Graph `fileSystemInfo`, defaulting btime to mtime when btime is missing to avoid creation time being overwritten. `Write` PATCHes item metadata and optionally writes permissions afterward.

Permission writes compare current and queued permissions. `sortPermissions` divides changes into add/update/remove, protects owner roles, handles business sharing-link update limitations by remove+add, supports add-only mode, and orders user permissions before group permissions. `processPermissions` removes first, then adds, then updates, accumulating non-retry errors. `addPermission` can create public anonymous links and otherwise sends `/invite` requests with recipients derived from identity fields.

Directory metadata creation uses `MkdirMetadata`: find or create the directory, send metadata during create when possible, then perform an extra write for modtime because OneDrive needs it. Existing directories are updated through `updateDir`.

## State And Persistence Behavior
Metadata is cached per `Object` or `Directory` in `meta`. Remote persistence occurs through Graph PATCH, invite, permission PATCH/DELETE, public link creation, and directory create requests. `queuedPermissions` is cleared only after successful refresh following writes. The `rwFailOK` option converts permission write errors into logged errors and nil returns.

The code does not keep a global metadata cache. Directory IDs come from `dirCache`, and `normalizedID` is required before permission operations. `Directory.SetModTime` preserves known btime or uses mtime as btime, then writes only timestamps.

## Dependencies And Integration Points
The file depends on OneDrive `api` DTOs, rclone metadata helpers, pacer/rest call helpers from the surrounding backend, dircache, error aggregation, and optional directory/object metadata interfaces. It is integrated into upload session creation, object metadata update after upload/copy, directory create/update, and public link behavior.

## Risks And Edge Cases
`api.Metadata.IsEmpty` pointer semantics can make empty metadata appear non-empty, causing `Write` to issue PATCHes with empty `FileSystemInfo`. `Set` counts `permissions` as set even if the decoded slice is empty; that can trigger permission removal behavior. Permission identity extraction maps non-email identities to `ObjectID` from `User.ID`, but group/site/application identities are temporarily copied into `User`, which is pragmatic but subtle. `Write` refuses to run when only permissions are queued but `toAPIMetadata` is empty; callers that want permissions-only writes should call `WritePermissions`. Public link creation inside `addPermission` can return a new permission-like object without a Graph invite if there are no recipients.

## Test Signals
The included tests cover `orderPermissions` for personal and business drive identity fields, including JSON from business `grantedToV2`. Missing focused tests include `Set` parsing, `toAPIMetadata` btime fallback, permission diff sorting for add/update/remove/owner/link cases, failok behavior, recipient extraction, directory metadata create/update, and permissions-only writes.
