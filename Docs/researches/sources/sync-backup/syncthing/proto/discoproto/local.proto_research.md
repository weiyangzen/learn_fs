# Research: sources/sync-backup/syncthing/proto/discoproto/local.proto

## sources/sync-backup/syncthing/proto/discoproto/local.proto

Purpose: defines the local discovery announce payload.

Important APIs/types: package `discoproto`; message `Announce` with raw device `id`, repeated `addresses`, and `instance_id`.

Control flow: schema-only; local discovery code broadcasts or receives generated announce messages.

State and persistence: no durable persistence implied. The message carries transient discovery state: device identity, reachable addresses, and instance identity to distinguish process restarts.

Dependencies and integration: integrates with local discovery networking and generated protobuf code. Risks include malformed address lists, raw device ID length assumptions, and compatibility if field numbers change. Test signal is generated-code compilation and local discovery integration tests.
