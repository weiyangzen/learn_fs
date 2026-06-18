# Research: sources/sync-backup/syncthing/proto/bep/bep.proto

## sources/sync-backup/syncthing/proto/bep/bep.proto

Purpose: defines the Block Exchange Protocol message schema used between Syncthing devices.

Important APIs/types: pre-auth `Hello`; message `Header`; enums for message type, compression, folder type, stop reason, file info type, response errors, and download progress updates; core messages `ClusterConfig`, `Folder`, `Device`, `Index`, `IndexUpdate`, `FileInfo`, `BlockInfo`, `Vector`, `Counter`, `PlatformData`, `Request`, `Response`, `DownloadProgress`, `Ping`, and `Close`.

Control flow: no executable flow; message flow is implicit in protocol sequencing: hello/header, cluster config, index updates, block requests/responses, progress, pings, and close.

State and persistence: `FileInfo` carries replicated file metadata, vector clocks, block hashes, platform metadata, and host-local fields with high field numbers. Reserved fields protect compatibility.

Dependencies and integration: imported by generated Go protocol code, database schemas, and network exchange logic. Risks are wire compatibility, semantic drift of host-local fields, reserved-field reuse, and enum default behavior. Test signals include protocol compatibility, generated code compilation, and integration sync tests that exchange these messages.
