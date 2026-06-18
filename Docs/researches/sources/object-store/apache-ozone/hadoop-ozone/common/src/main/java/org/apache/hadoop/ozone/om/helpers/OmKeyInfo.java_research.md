# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyInfo.java

Purpose: Authoritative key metadata model for OM key/open-key/deleted-key tables and key RPC responses.

Important APIs/types/functions: Extends `WithParentObjectId`, implements `Auditable` and `CopyObject`. `CODEC` persists `KeyInfo` protobuf with pipeline omitted for DB storage. Fields include volume, bucket, key name, size, key-location versions, times, replication config, encryption info, checksum, file flag/name, owner, ACLs, tags, metadata, object/update/parent IDs, and expected generation. Core methods include `updateLocationInfoList`, `appendNewBlocks`, `addNewVersion`, `getProtobuf`, `getNetworkProtobuf`, `builderFromProtobuf`, conversion to/from `OmDirectoryInfo`, and ETag helpers.

Control flow and state: Commit-time `updateLocationInfoList` verifies committed block IDs against allocated blocks unless explicitly skipped, returns uncommitted allocations for deletion, replaces latest-version blocks, and marks multipart status. `appendNewBlocks` mutates the latest version; `addNewVersion` appends a new version or clears old versions based on `keepOldVersions`. Several setters mutate key name, size, modification time, replication config, encryption info, and expected generation.

State and persistence behavior: Persisted as `KeyInfo` protobuf in OM RocksDB. DB serialization can ignore pipelines, while network serialization includes them and can include only latest version blocks. Metadata, tags, ACLs, object IDs, parent IDs, encryption info, checksums, and replication config round trip through protobuf.

Dependencies and integration points: Central to key create/commit/read/delete, FSO directories, snapshots, replication/quota accounting, block token/pipeline return, and multipart part conversion. Depends on HDDS block/location classes, Ozone ACL/protobuf helpers, replication configs, checksums, encryption, and codecs.

Risks: The class is mutable and often shared through table/cache layers; copy discipline matters. Block verification compares container block IDs only, intentionally ignoring pipeline/BCS differences. `equals`/`hashCode` are narrower than full metadata identity. Missing replication config or malformed location versions can fail serialization.

Test signals: Codec round trips with/without pipelines, EC and legacy replication, encrypted keys, ACL/tag/metadata persistence, block commit verification and uncommitted-block return, append/new-version behavior, latest-version network serialization, FSO directory conversion, ETag helpers, and copy-object isolation.
