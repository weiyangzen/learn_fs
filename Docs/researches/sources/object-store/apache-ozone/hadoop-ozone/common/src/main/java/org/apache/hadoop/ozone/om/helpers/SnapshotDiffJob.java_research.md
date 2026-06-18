<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotDiffJob.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotDiffJob.java

## Purpose

`SnapshotDiffJob` is the persisted status record for asynchronous snapshot diff jobs. It records job identity, snapshot pair, options, status/sub-status, progress, entry counts, largest key, and failure reason.

## Important APIs, Types, And Functions

Important methods include `codec`, getters/setters, `toString`, `equals`, `hashCode`, `toProtoBuf`, `getFromProtoBuf`, and the private `SnapshotDiffJobCodec`. The codec writes protobuf and falls back to old Jackson JSON when protobuf parsing fails.

## Control Flow, State, And Persistence

OM creates and updates this object as diff jobs move through queued/in-progress/done/failed states. The codec persists to the snapshot diff job table as `SnapshotDiffJobProto`. Fallback JSON decoding preserves upgrade compatibility with older persisted rows.

## Dependencies And Integration Points

It depends on Jackson, protobuf, HDDS `Codec`, `SnapshotDiffJobProto`, and snapshot diff `JobStatus`/`SubStatus`. It integrates with `OzoneManagerProtocol.submitSnapshotDiff`, `cancelSnapshotDiff`, `listSnapshotDiffJobs`, background diff services, and diff progress reporting.

## Risks And Test Signals

`copyObject` returns the same object despite mutability. `toString` calls `status.equals(...)`, so null status can fail. Tests should cover protobuf and legacy JSON decode, all status/sub-status combinations, progress formatting, failure reason persistence, equality/hash changes, and concurrent updates in DB cache paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotDiffJob.java -->
