# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneConfigUtil.java

Purpose: `OzoneConfigUtil` provides small server-side configuration helpers for OM code, currently replication-config preference resolution and capping client-provided numeric limits against server limits.

Important APIs/types/functions: `resolveReplicationConfigPreference` chooses a `ReplicationConfig` from client protobuf fields, bucket defaults, or OM defaults. `limitValue` caps a client numeric configuration value to a server maximum and enforces a minimum usable page size of two. The class is a final static utility with an SLF4J logger.

Control flow: Replication resolution first checks whether the client supplied a replication type other than `HddsProtos.ReplicationType.NONE`. If so, it builds a `ReplicationConfig` from the client type, factor, and EC config, then asks `OzoneManager.validateReplicationConfig` to reject unsupported choices. If the client supplied no type and the bucket has a `DefaultReplicationConfig`, that bucket default wins. If neither client nor bucket default is present, the method returns `ozoneManager.getDefaultReplicationConfig()`. `limitValue` starts with the client value, caps it to the server value when it exceeds the server limit, logs the cap at debug level, then raises any result less than or equal to one to two.

State and persistence behavior: There is no mutable state or persistence. The returned replication config may come from the supplied bucket object or OM default, and validation side effects are limited to `OzoneManager.validateReplicationConfig`.

Dependencies/integration points: It depends on HDDS replication model classes (`ReplicationConfig`, `DefaultReplicationConfig`, `HddsProtos`) and `OzoneManager` for validation/defaults. `limitValue` is designed for paged/list-style server APIs where client limits must not exceed server-supported limits and where page size one can cause a non-recursive `listStatus` loop involving `startKey`.

Risks: Client replication preference bypasses bucket defaults by design, so validation must be kept strong enough to prevent unsupported configs. `limitValue` applies the minimum of two after max capping, which means a server limit of zero or one still results in two; callers must only use it for APIs where that lower bound is valid. The page-size loop comment is specific to file-status/listStatus behavior and should not be generalized blindly to unrelated numeric configs.

Test signals: `TestOzoneConfigUtil` covers EC bucket defaults, server defaults, client EC preference, and RATIS bucket defaults. The searched tests do not directly cover `limitValue`; listStatus and file-status paging tests provide indirect signal for the minimum page-size behavior.
