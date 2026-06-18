# sources/object-store/minio/cmd/storage-rest-common.go

Purpose: defines the shared storage REST protocol constants and msgp payload structs used by both the remote storage client and server.

Important APIs/types/functions: `storageRESTVersion` is `v63`, with a comment noting the introduction of `RenamePart` and `ReadParts`. `storageRESTPrefix` mounts the storage API under MinIO's reserved bucket path. Method constants define compact endpoint suffixes for health, append/create/read/delete/rename/stat/verify/bulk APIs. Query/form constants define compact keys such as `vol`, `fp`, `did`, `offset`, `length`, `incl-fv`, and bitrot fields. `nsScannerOptions` carries disk ID, scan mode, and a `dataUsageCache`; `nsScannerResp` carries either an incremental `dataUsageEntry` update or final cache.

Control flow: this file has no executable flow beyond constants and type definitions. Its values are consumed by `storage-rest-client.go` while constructing HTTP query strings and by `storage-rest-server.go` while parsing requests and registering routes. The two scanner structs are serialized by generated msgp code for the streaming namespace scanner RPC.

State and persistence behavior: no persistent state is stored here. Protocol version and field names are compatibility state: changing them requires coordinated client/server updates across a cluster.

Dependencies/integration: depends on MinIO reserved path constants and data scanner structs. It is tightly coupled with generated code in `storage-rest-common_gen.go`, generated tests, the storage REST server route table, and remote disk client methods.

Risks/test signals: compact path names are easy to collide; notably both `storageRESTMethodReadFile` and `storageRESTMethodRenameFile` are `"/rfile"`, but they are distinguished by HTTP method/grid use in practice. Protocol additions need version bumps and generated msgp refreshes. Generated msgp tests cover scanner payload serialization, while storage REST integration tests validate a subset of route behavior.
