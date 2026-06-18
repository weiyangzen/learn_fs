## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationConfig.java

Purpose: Tests `ReplicationServer.ReplicationConfig` configuration parsing, defaulting, and bounds enforcement.

Important APIs/types/functions: `ReplicationConfig.getReplicationMaxStreams`, `getOutOfServiceFactor`, config keys `REPLICATION_STREAMS_LIMIT_KEY` and `REPLICATION_OUTOFSERVICE_FACTOR_KEY`, and constants for defaults/min/max.

Control flow: Tests valid values, invalid negative stream limit fallback, out-of-service factor clamping below min/above max, exact boundary acceptance, and default object creation from an empty `OzoneConfiguration`.

State and persistence behavior: In-memory configuration only.

Dependencies and integration points: Drives `ReplicationSupervisor` pool and queue scaling behavior, especially during decommission/maintenance states.

Risks and test signals: Good guard for operational config safety. It does not test live reconfiguration directly; that appears in `TestReplicationSupervisor`.
