# sources/sync-backup/syncthing/internal/db/observed.go

## Purpose
This file implements storage for observed but not yet accepted devices and folders. It backs pending devices/folders shown in the GUI and API, using the generic database `KV` interface.

## Important APIs, Control Flow, And State
`ObservedDB` wraps `KV`. `ObservedFolder` stores time, label, receive-encrypted, and remote-encrypted flags and converts to/from protobuf wire types. `ObservedDevice` stores time, name, and address. `AddOrUpdatePendingDevice` writes `device/<deviceID>`, `RemovePendingDevice` deletes it, and `PendingDevices` enumerates `device/` keys, parsing device IDs and protobuf values. Folder methods use keys `folder/<deviceID>/<folderID>`; they can add/update, remove a specific folder/device pair, remove all offers for a folder, list all pending folders, or list only those for one device. Invalid entries are deleted as a side effect during enumeration.

## State And Persistence
State is persisted in the generic KV store as protobuf-encoded `dbproto.ObservedDevice` and `dbproto.ObservedFolder` values. Times are truncated to seconds when adding pending devices and stored as protobuf timestamps.

## Dependencies And Integration Points
It depends on `dbproto`, `protocol.DeviceID`, protobuf marshal/unmarshal, and `timestamppb`. It integrates with cluster pending-device/folder REST endpoints and GUI pending maps.

## Risks And Test Signals
Enumeration repairs invalid keys by deleting them, which is practical for ephemeral pending state but means read paths mutate storage. `RemovePendingFolder` scans all folder entries and deletes matching folder IDs across devices. The `mustMarshal` helper panics on marshal failure, acceptable for generated protobuf messages but still a hard failure. Tests should cover invalid key cleanup, invalid protobuf cleanup, per-device filtering, all-device removal, and JSON field compatibility.
