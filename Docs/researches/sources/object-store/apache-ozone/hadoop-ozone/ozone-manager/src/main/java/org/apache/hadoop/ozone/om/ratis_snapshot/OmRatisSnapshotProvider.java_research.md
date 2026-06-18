# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/OmRatisSnapshotProvider.java

## Purpose
`OmRatisSnapshotProvider` downloads OM DB checkpoints from the current leader for follower bootstrap/catch-up and wraps the downloaded DB as a RocksDB checkpoint. It also supports transferring leader-created OM snapshots that must exist on followers.

## Important APIs and Types
- Constructors initialize snapshot directory, peer map, HTTP policy, SPNEGO mode, URL connection factory, and whether to use the v2 inode-based checkpoint API.
- `addNewPeerNode` and `removeDecommissionedPeerNode` update the peer map.
- `downloadSnapshot(String leaderNodeID, File targetFile)` performs the HTTP POST download.
- `downloadFileWithProgress` streams the response to disk and logs progress.
- `getCheckpointFromUntarredDb` returns an `InodeMetadataRocksDBCheckpoint`.
- `writeFormData` writes multipart form-data listing SST files to exclude.
- `close` destroys the connection factory.

## Control Flow
The configuration constructor reads HTTP policy, Kerberos/SPNEGO setting, connection timeout, request timeout, and the inode-based checkpoint flag. `downloadSnapshot` looks up leader node details, builds the OM DB checkpoint endpoint URL, opens an authenticated connection as the current user, sets multipart POST headers, computes existing files from the candidate directory, writes exclusion form data, and connects. It accepts HTTP 200 and 201. The response body is streamed to `targetFile`; if streaming fails, the partial target is deleted quietly and the exception is rethrown. The connection is disconnected in a finally block.

`writeFormData` emits one multipart field per SST/existing file using the configured multipart boundary. If there are no files, it still writes an empty field. `getCheckpointFromUntarredDb` wraps the untarred directory in an inode-aware checkpoint so later install code can reason about v1/v2 checkpoint layout.

## State and Persistence Behavior
The provider persists downloaded checkpoint archives/files into the snapshot provider’s candidate/target directories managed by `RDBSnapshotProvider`. It does not directly install the DB into OM; the state machine and OM install logic consume the checkpoint. Peer-node state is held in a concurrent map.

## Dependencies and Integration Points
It extends `RDBSnapshotProvider`, depends on `OMNodeDetails` for endpoint URLs, `URLConnectionFactory`, Hadoop security `SecurityUtil`, `HAUtils` for existing-file lists, `HttpConfig.Policy`, Apache Commons `FileUtils`, and `InodeMetadataRocksDBCheckpoint`. `OzoneManagerStateMachine.notifyInstallSnapshotFromLeader` triggers snapshot installation through OM, which uses this provider.

## Risks and Edge Cases
Missing leader node id causes a null dereference before URL creation. Large downloads rely on streaming and progress logs every 30 seconds. Partial file cleanup logs but does not fail if deletion itself fails. Multipart formatting must match the OM checkpoint endpoint. SPNEGO and HTTP policy misconfiguration can make follower catch-up fail. Concurrent peer map updates are safe at map level but do not validate role/service consistency.

## Test Signals
Tests should cover endpoint URL selection for v1/v2 checkpoint API, multipart body with empty and non-empty exclusion lists, HTTP error handling, partial download cleanup, SPNEGO connection path, peer add/remove, progress streaming, and checkpoint wrapper construction.
