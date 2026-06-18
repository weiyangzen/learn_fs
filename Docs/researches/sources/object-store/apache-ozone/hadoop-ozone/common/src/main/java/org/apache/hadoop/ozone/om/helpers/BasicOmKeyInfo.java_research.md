# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BasicOmKeyInfo.java

Purpose: Lightweight key metadata used by light/list-key responses where full block locations and rich `OmKeyInfo` state are unnecessary.

Important APIs/types/functions: Fields include volume, bucket, key, size, times, replication config, file flag, ETag, owner, and encryption flag. `Builder` constructs instances. `fromOmKeyInfo` extracts a light view from full metadata. `getProtobuf` serializes to `BasicKeyInfo`; overloaded `getFromProtobuf` methods reconstruct using either `ListKeysRequest` or explicit volume/bucket names.

Control flow and state: The object is mostly immutable after construction except `ownerName` is not final. Proto conversion writes EC replication config or legacy factor depending on replication type. When older protos lack `isFile`, parsing infers file status from whether the key name ends in `/`.

State and persistence behavior: This is a transport DTO, not the primary OM DB value. It preserves replication and encryption indicators needed by clients while omitting block lists.

Dependencies and integration points: Depends on `ReplicationConfig`, `ECReplicationConfig`, `QuotaUtil`, `OmKeyInfo`, and Ozone Manager protobuf `BasicKeyInfo`. Used by `ListKeysLightResult` and list-key RPC flows.

Risks: `equals` assumes non-null volume, bucket, key, replication config, and owner; partially built instances can throw. `hashCode` uses only names while `equals` includes more fields, which is legal but collision-prone.

Test signals: Round-trip proto tests should include EC and RATIS/STAND_ALONE replication, blank and nonblank ETag, missing `isFile`, encrypted flag, owner propagation, and replicated-size calculation.
