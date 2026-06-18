# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBCheckpointServletInodeBasedXferNonLeader.java

Purpose: Focused servlet tests for `OMDBCheckpointServletInodeBasedXfer` when the local OM is not leader-ready. It protects checkpoint download paths from serving snapshots from followers or unready leaders.

Important APIs and types: `OMDBCheckpointServletInodeBasedXfer`, `processMetadataSnapshotRequest`, `OzoneManager.isLeaderReady`, servlet context attribute `OzoneConsts.OM_CONTEXT_ATTRIBUTE`, `HttpServletRequest`, and `HttpServletResponse`.

Control flow: each test spies the servlet to inject a mocked `ServletContext`, returns a mocked OM with `isLeaderReady=false`, invokes `processMetadataSnapshotRequest`, and verifies response handling. One path checks normal `sendError(503, message)`; the other forces `sendError` to throw and verifies fallback `setStatus(503)`.

State and persistence: no durable state is created. The only state is the servlet context and response status/error side effect.

Dependencies and integration points: integrates with OM HTTP checkpoint transfer and servlet containers. It assumes the servlet obtains OM from context and performs leader gating before snapshot streaming.

Risks and edge cases: broken clients may cause `sendError` to throw; without fallback status setting the HTTP response could look successful. A regression could allow non-leaders to serve stale metadata snapshots.

Test signals: Mockito verifies exact service-unavailable response behavior and fallback status assignment.
