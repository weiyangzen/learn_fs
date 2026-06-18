# sources/object-store/minio-mc/cmd/client-fs_windows.go

## Purpose

This Windows-specific file adapts filesystem watch events and metadata behavior to Windows. It enables the shared filesystem client to compile and classify common create/delete/read notifications while disabling xattr preservation.

## Important APIs, Control Flow, And State

`EventTypePut` includes create/write/rename and Windows file-name/directory-name change events. `EventTypeDelete` includes remove, while get uses `FileNotifyChangeLastAccess`. `IsPutEvent` specially excludes `FileActionRenamedOldName` so rename-away is not mistaken for a put. `IsDeleteEvent` treats both remove and renamed-old-name as deletion. `getAllXattrs` returns nil metadata because Windows xattr support is not implemented here.

## Dependencies, Integration, Risks, And Tests

The only dependency is `notify`. The file feeds `fsClient.Watch` and preserve-mode metadata calls. Risks include Windows rename event ambiguity, last-access notifications depending on filesystem settings, lack of chmod policy support in `client-fs.go`, and no xattr preservation. `client-fs_test.go` explicitly skips chmod access validation on Windows and the main filesystem tests indirectly validate build compatibility.
