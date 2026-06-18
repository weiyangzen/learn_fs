<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocolServerSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocolServerSideTranslatorPB.java

Purpose: `ScmBlockLocationProtocolServerSideTranslatorPB` adapts block-location protobuf RPCs to the SCM block-location implementation. It covers block allocation, key-block deletion, SCM info, adding SCMs, datanode sorting, and network topology retrieval.

Important APIs and types: It implements `ScmBlockLocationProtocolPB` with `send` and `processMessage`. Helpers include `allocateScmBlock`, `deleteScmKeyBlocks`, `getScmInfo`, `getAddSCMResponse`, `sortDatanodes`, and `getClusterTree`. It converts `ReplicationConfig`, `ExcludeList`, `AllocatedBlock`, `BlockGroup`, and `DeleteBlockGroupResult`.

Control flow: `send` requires SCM leadership and dispatches through `OzoneProtocolMessageDispatcher`. `processMessage` switches on command type, applies an EC upgrade-finalization gate to block allocation, builds command-specific responses, and maps `IOException` to status. Allocation verifies that the implementation returns as many blocks as requested.

State and persistence behavior: The translator has no durable state. Allocated block and deletion state is managed by `ScmBlockLocationProtocol`. It passes client version into pipeline and datanode protobuf conversions for compatibility.

Dependencies and integration points: It integrates OM/client block allocation with SCM container and pipeline state, upgrade finalization, HA leader checks, topology sorting, and protocol metrics.

Risks: EC allocation is blocked until layout finalization allows EC support. `sortDatanodes` wraps IO failures in `ServiceException` while most switch failures become response statuses, so callers see mixed error styles. Allocation treats partial success as an exception after the implementation has potentially allocated some blocks.

Test signals: Tests should cover leader rejection, EC pre-finalization rejection, partial allocation failure, correct pipeline protobuf ports, delete result conversion, add-SCM status, datanode sort conversion, topology serialization, and exception status mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocolServerSideTranslatorPB.java -->
