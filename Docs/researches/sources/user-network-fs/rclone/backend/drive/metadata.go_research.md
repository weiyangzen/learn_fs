# sources/user-network-fs/rclone/backend/drive/metadata.go

## Purpose
`metadata.go` implements Drive metadata read/write support for rclone. It documents system metadata keys, augments Drive field selection, reads owners/permissions/labels/folder attributes into `fs.Metadata`, writes supported metadata back into Drive API request structs, and creates post-upload callbacks for metadata that cannot be set in the initial file create/update request.

## Important APIs, types, and functions
- `systemMetadataInfo` describes Drive-owned metadata keys such as `content-type`, `mtime`, `btime`, sharing flags, owner, permissions, folder color, description, starred, and labels.
- `metadataFields`, `permissionsFields`, and `labelsFields` define extra Drive API fields required for metadata-aware listing/getting.
- `getPermission`, `setPermissions`, `cleanPermissionForWrite`, `cleanAndCachePermission`, and `cleanPermission` read, cache, sanitize, and write Drive permissions.
- `getLabels`, `setLabels`, `labelFieldsToFieldModifications`, and `cleanLabel` read labels and translate label field values into Drive `ModifyLabelsRequest` structures.
- `baseObject.parseMetadata` converts a Drive `File` into rclone metadata, including user `Properties` and selected system metadata.
- `setOwner`, `updateMetadata`, and `fetchAndUpdateMetadata` apply metadata during create/update workflows and return callbacks for owner, permissions, and labels.

## Control flow
Read flow starts when `drive.go` includes `metadataFields` in file fields and calls `parseMetadata`. User properties are copied first so they can override or coexist with system values. System booleans, MIME type, owner, permissions, folder color, description, starred, creation time, modification time, and labels are then inserted depending on configured read modes. Permission reading may use already returned `Permissions`, or fetch individual `PermissionIds` concurrently through an `errgroup` limited by `ci.Checkers`; inherited shared-drive permissions and owner permissions are excluded from serialized metadata.

Write flow starts in `fetchAndUpdateMetadata`, which reads source metadata through rclone metadata options and calls `updateMetadata`. That function walks each key, mutates the Drive `File` request for fields that can be set directly, places unknown keys into `Properties`, and appends callbacks for owner transfer, permissions creation, and labels modification. The caller executes the callback after upload/update returns an actual Drive file ID.

## State and persistence behavior
Permissions are cached in `Fs.permissions` under `permissionsMu` by permission ID after cleaning output-only fields. Label and permission writes persist to Drive through Drive API calls after upload. User metadata persists in Drive `properties`. Creation time can only be set on fresh uploads, while modification time can be set on updates. `MetadataOwner`, `MetadataPermissions`, and `MetadataLabels` bit flags control read/write/failok behavior independently.

## Dependencies and integration points
This file depends on `fs.Metadata`, rclone metadata option helpers, `fserrors.NoRetryError`, `errcount`, `errgroup`, and Google Drive API permission/label/file structs. It is called from object construction, metadata getters, `createDir`, `updateDir`, `PutUnchecked`, `Object.Update`, and `Copy` in `drive.go`.

## Risks and edge cases
- Permission metadata can be expensive: shared drives may require per-permission fetches to determine inheritance.
- Owner transfer has policy and notification constraints and can fail after file upload; `failok` controls whether that fails the transfer.
- Permissions and labels are post-upload callbacks, so partial metadata application is possible if later callbacks fail.
- Label writes require pre-existing label/field IDs; this code maps values but does not create label definitions.
- Boolean and JSON metadata parsing errors abort updates unless the key's feature is disabled.
- Unknown metadata keys become Drive user properties, which could collide with user-supplied keys.

## Test signals
Drive integration tests indirectly exercise metadata through upload/copy/update flows when metadata is enabled. The code itself includes no standalone tests in this subset, so high-risk paths such as permission inheritance filtering, label modification, and owner transfer depend on broader integration coverage or manual Drive API validation.
