# Research: sources/sync-backup/syncthing/proto/apiproto/tokenset.proto

## sources/sync-backup/syncthing/proto/apiproto/tokenset.proto

Purpose: defines API token-set persistence/serialization schema.

Important APIs/types: package `apiproto`; message `TokenSet` with `map<string, int64> tokens = 1`, documenting token to expiry time in epoch nanoseconds.

Control flow: no executable control flow; generated code will provide marshaling, unmarshaling, and map accessors.

State and persistence: represents persistent or wire-serialized API token expiry state. Field number 1 is the compatibility contract.

Dependencies and integration: uses proto3 map semantics and integrates with generated Go code for API authentication/token management. Risks are time-unit confusion and schema compatibility if field numbers or types change. Test signals are generated-code compilation and API/token tests elsewhere.
