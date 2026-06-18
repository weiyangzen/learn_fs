## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMAdminProtocolServerSideImpl.java

Purpose: protobuf server-side translator for OM admin RPCs.

Important APIs and types: implements `OMAdminProtocolPB`; methods are `getOMConfiguration`, `decommission`, `compactDB`, and `triggerSnapshotDefrag`.

Control flow: configuration returns OM nodes in current memory and new configuration. Decommission validates non-null request, checks leader status, resolves the peer node, enforces admin authorization when enabled, and asks Ratis to remove the OM. Compact validates the column-family table exists before calling `ozoneManager.compactOMDB`. Snapshot defrag delegates to `ozoneManager.triggerSnapshotDefrag(noWait)`. RPC methods convert IO failures into protobuf responses with `success=false` and an error string.

State and persistence: the translator owns only an `OzoneManager` reference. Effects happen in OM/Ratis: membership changes, DB compaction, and snapshot defrag triggering.

Dependencies and integration: server adapter for admin clients, Ratis utilities, admin authorization via remote user, OM metadata store, and snapshot defrag service.

Risks and test signals: `decommission` returns null for null request, which is unusual for PB services. Decommission checks leader before authorization. Compact can expose table names and compaction cost through admin RPC. Tests should cover node list serialization, unknown peer, non-admin denial, leader checks, removeOM IO errors, valid/invalid column family compaction, defrag success/failure, and null request behavior.
