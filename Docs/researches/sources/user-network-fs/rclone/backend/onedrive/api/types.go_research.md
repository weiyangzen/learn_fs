# sources/user-network-fs/rclone/backend/onedrive/api/types.go

## Purpose
`types.go` defines Go representations for Microsoft Graph OneDrive API resources and request/response payloads used by rclone's OneDrive backend. It includes error formatting, identity and quota structures, drive/item/folder/file facets, timestamps, sharing and permission types, upload/copy/move/share request bodies, delta/list responses, version/site/drive responses, and normalization helpers for remote shared items.

## Important APIs, Types, And Functions
Key exports include `Error`, `Identity`, `IdentitySet`, `Quota`, `Drive`, `Timestamp`, `ItemReference`, `RemoteItemFacet`, `FolderFacet`, `HashesType`, `FileFacet`, `FileSystemInfoFacet`, `DeletedFacet`, `PackageFacet`, `SharedType`, `SharingInvitationType`, `SharingLinkType`, `PermissionsType`, `Role`, `PermissionsResponse`, `AddPermissionsRequest`, `UpdatePermissionsRequest`, `DriveRecipient`, `Item`, `Metadata`, `DeltaResponse`, `ListChildrenResponse`, create/upload/copy/move/share request and response structs, `AsyncOperationStatus`, version and site/drive response types.

Behavioral helpers include `Error.Error`, `Timestamp.MarshalJSON`, `Timestamp.UnmarshalJSON`, `ItemReference.GetID`, `Metadata.IsEmpty`, many `Item.Get*` normalizers, `Item.MalwareDetected`, `Item.IsRemote`, and permission accessors `PermissionsType.GetGrantedTo` and `GetGrantedToIdentities`.

## Control Flow
The file is mostly declarative. JSON marshaling/unmarshaling flows through struct tags. `Timestamp` uses a fixed millisecond UTC format. `Item` helper methods prefer `RemoteItem` fields when present and populated, otherwise fall back to direct item fields. ID helpers prefix item IDs with drive IDs when a normalized ID is needed and the ID does not already contain `#`.

## State And Persistence Behavior
There is no runtime state. These structs are transient data transfer objects for Graph API calls. The only persistence implication is JSON shape compatibility with Microsoft Graph and rclone's metadata code.

## Dependencies And Integration Points
The file is used across the OneDrive backend for listing, metadata, permissions, uploads, moves, copies, deltas, public links, versions, and drive/site discovery. `metadata.go` relies heavily on `Metadata`, `PermissionsType`, role constants, recipient request structs, `FileSystemInfoFacet`, and item normalization helpers.

## Risks And Edge Cases
`Metadata.IsEmpty` compares `m.FileSystemInfo == &FileSystemInfoFacet{}`, which compares pointers rather than pointed-to contents. A newly allocated empty `FileSystemInfoFacet` is therefore not considered empty, so callers may issue metadata PATCH calls with empty fileSystemInfo. This may be intentional to force timestamp bodies, but the name is misleading. Timestamp parsing accepts only the exact millisecond format used in `timeFormat`, so Graph variants without milliseconds could fail if used for these fields. Remote item fallback is field-by-field and can miss valid zero values, such as remote size 0.

## Test Signals
This file has no direct tests in the listed set. Good coverage would include timestamp round trips, `Error.Error` with and without inner codes, normalized ID behavior, remote item getters, permission accessor differences between personal and business drives, and `Metadata.IsEmpty` semantics.
