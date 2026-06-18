# sources/sync-backup/syncthing/internal/gen/bep/bep.pb.go

## Purpose
This generated protobuf file defines Syncthing's Block Exchange Protocol message and enum types used on the wire and in database serialization.

## Important APIs and Types
Enums include `MessageType`, `MessageCompression`, `Compression`, `FolderType`, `FolderStopReason`, `FileInfoType`, `ErrorCode`, and `FileDownloadProgressUpdateType`. Message structs include handshake/control messages (`Hello`, `Header`, `Ping`, `Close`), cluster configuration (`ClusterConfig`, `Folder`, `Device`), index exchange (`Index`, `IndexUpdate`, `FileInfo`, `BlockInfo`, `Vector`, `Counter`), platform metadata (`PlatformData`, `UnixData`, `WindowsData`, `XattrData`, `Xattr`), block transfer (`Request`, `Response`), and progress (`DownloadProgress`, `FileDownloadProgressUpdate`). Each generated type has standard protobuf reset/string/reflection/descriptor methods and nil-safe getters.

## State and Persistence Behavior
This file does not persist data directly, but its `FileInfo`, `BlockInfo`, and `Vector` wire shapes are persisted by the SQLite database as `fileinfos.fiprotobuf`, external blocklist protobufs, and version strings/conversions. Some fields are host-local implementation details (`local_flags`, `version_hash`, `encryption_trailer_size`) and are not intended for wire exchange despite being present in the generated struct.

## Dependencies and Integration Points
It depends on protobuf runtime/reflection packages. The SQLite code uses `bep.FileInfo` in `indirectFI.FileInfo` and `protocol.FileInfo.ToWire`/`FromDB`; protocol networking layers use the full message set.

## Risks and Test Signals
The file is generated and should not be manually edited. Changing proto field numbers, defaults, or local-only fields can break network compatibility or database decoding. SQLite tests indirectly cover `FileInfo` and `BlockInfo` persistence through update/retrieval and blocklist behavior.
