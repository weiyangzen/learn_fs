# Research: sources/sync-backup/syncthing/proto/discosrv/discosrv.proto

## sources/sync-backup/syncthing/proto/discosrv/discosrv.proto

Purpose: defines discovery server database and replication records.

Important APIs/types: package `discosrv`; `DatabaseRecord`, `ReplicationRecord`, and `DatabaseAddress`. Addresses carry a string address and expiration time in Unix nanoseconds; records carry last-seen time and, for replication, the raw 32-byte device ID key.

Control flow: schema-only. Server code stores, serves, and replicates records using generated serialization.

State and persistence: explicitly persistent discovery database state and replication payloads.

Dependencies and integration: discovery server database/replication layers depend on field compatibility. Risks include time-unit mistakes, expired address retention, and raw key length assumptions. Test signal is generated-code compilation and discovery server tests.
