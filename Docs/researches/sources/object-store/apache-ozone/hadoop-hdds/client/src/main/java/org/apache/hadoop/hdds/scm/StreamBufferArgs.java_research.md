# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/StreamBufferArgs.java

Purpose: Immutable-by-convention argument bundle for Ozone client stream buffer sizing.

Important APIs/types/functions: Holds buffer size, flush size, max size, and flush-delay flag. Builder exposes setters and `build()`. `getDefaultStreamBufferArgs(ReplicationConfig, OzoneClientConfig)` chooses values based on replication type.

Control flow: For EC replication, buffer, flush, and max sizes all become the EC chunk size from `ECReplicationConfig`. For non-EC replication, values come from `OzoneClientConfig`. Flush-delay always comes from client config.

State and persistence behavior: Stores buffer parameters in memory. Setters are protected except flush-delay setter is public, so the object is not strictly immutable.

Dependencies and integration points: Used by stream writing code to derive buffer pool behavior. Depends on replication configs and `HddsProtos.ReplicationType`.

Risks: The EC branch casts `ReplicationConfig` to `ECReplicationConfig` after checking type; custom configs must obey that contract. No validation is performed in the builder, so invalid sizes must be caught elsewhere.

Test signals: Tests should cover EC and non-EC defaults, flush-delay propagation, and builder setter behavior.
