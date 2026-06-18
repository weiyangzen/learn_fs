# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotDiffJobResponse.java

Purpose: DTO for paginated list-snapshot-diff-job API responses.

Important APIs and types: Final class with `List<SnapshotDiffJob>` and optional `lastSnapshotDiffJob` continuation marker. Provides getters and `toString`.

Control flow: Constructor assigns fields; no transformation or validation.

State and persistence behavior: In-memory response wrapper. Snapshot diff job persistence is maintained server-side.

Dependencies and integration points: Built by the OM client translator from `ListSnapshotDiffJobResponse` protobufs and consumed by CLI/client code for pagination.

Risks: The list is not defensively copied, so caller mutations can alter the response object. Continuation marker null means no explicit next page.

Test signals: Verify protobuf-to-DTO conversion in translator, continuation marker behavior, and string rendering.
