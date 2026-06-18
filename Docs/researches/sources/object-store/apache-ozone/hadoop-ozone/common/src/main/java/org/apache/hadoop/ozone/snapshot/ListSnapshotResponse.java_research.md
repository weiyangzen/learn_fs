# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/snapshot/ListSnapshotResponse.java

Purpose: DTO for paginated snapshot listing responses.

Important APIs and types: Holds `List<SnapshotInfo>` and optional `lastSnapshot` marker, with getters and `toString`.

Control flow: Constructor assigns fields. Pagination compatibility logic is in the client translator, not this class.

State and persistence behavior: In-memory wrapper over server-provided snapshot info. It does not persist snapshot state.

Dependencies and integration points: Returned by `OzoneManagerProtocolClientSideTranslatorPB.listSnapshot` and used by clients/CLI to continue listing from `lastSnapshot`.

Risks: Snapshot list is not defensively copied. Null `lastSnapshot` must be interpreted as no continuation marker.

Test signals: Translator tests should cover explicit marker, fallback marker generation when server lacks marker and page is full, and no marker when list is short.
