# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBuffer.java

Purpose: tests snapshot-aware flushing, metrics, async flush notification, and S3 secret cache cleanup in `OzoneManagerDoubleBuffer`.

Important APIs/types: `OzoneManagerDoubleBuffer`, `FlushNotifier`, `OzoneManagerDoubleBufferMetrics`, `OMClientResponse`, snapshot/key/bucket response mocks, `TransactionInfo`, `S3GetSecretRequest`, `S3SecretLockedManager`, `S3SecretCache`, and `OmMetadataManagerImpl`.

Control flow: setup builds a temporary OM metadata manager and double buffer with mocked OM responses and a spied flush notifier. Parameterized cases stop the daemon, add response sequences, manually flush, and assert flush iteration counts and metrics. Snapshot create/purge responses force split flushing behavior. `testAwaitFlush` wires notifier answers to assert buffers are empty when notified and verifies repeated await semantics. S3 secret testing creates successful `GetS3Secret` requests, confirms cache population, flushes, and asserts cache entries are cleared.

State and persistence behavior: uses a real temporary metadata store, but most response DB updates are mocked no-ops except S3 secret request paths. Metrics are static/shared enough that expected totals account for cumulative state and are explicitly reset in places. Flush state spans current/ready buffers and transaction counts.

Dependencies and integration points: integrates OM metadata, audit logging, S3 secret manager/cache, Kerberos principal shortening, response classes, and double-buffer internals.

Risks: metric expectations can be brittle because metrics are shared. Manual daemon stopping avoids races but differs from production timing. Some mocked snapshot responses report `SnapshotPurge` for create mocks, so the test targets splitting semantics more than command identity.

Test signals: validates snapshot-aware split counts, flush transaction metrics, await/notify behavior, empty-buffer await, and post-flush S3 cache eviction.
