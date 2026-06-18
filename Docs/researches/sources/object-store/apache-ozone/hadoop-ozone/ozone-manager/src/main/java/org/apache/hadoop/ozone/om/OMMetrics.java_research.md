# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMetrics.java

## Purpose
`OMMetrics` is the Ozone Manager metrics source. It registers mutable counters and gauges for OM operations, failures, object counts, filesystem operations, multipart uploads, snapshots, multi-tenancy, trash, erasure coding, linearizable reads, follower reads, open-key cleanup, expired MPU cleanup, DB checkpointing, and recent Ratis events.

## Important APIs, types, and functions
The class is annotated `@Metrics` and implements `OmMetadataReaderMetrics`. Fields annotated with `@Metric` are Hadoop metrics2 `MutableCounterLong` or `MutableGaugeInt` instances. `create(ConfigurationSource)` registers an `OMMetrics` instance with the `DefaultMetricsSystem` using a configured max Ratis event count. `getDBCheckpointMetrics` exposes a nested `DBCheckpointMetrics` source. `startSnapshotDirectoryMetrics` and `stopSnapshotDirectoryMetrics` manage an `OMSnapshotDirectoryMetrics` helper.

Most methods are direct incrementers or getters. Incrementers often update both a category counter, such as `numKeyOps`, `numBucketOps`, `numVolumeOps`, `numFSOps`, or `numTenantOps`, and a specific operation counter. Setters such as `setNumVolumes`, `setNumBuckets`, `setNumKeys`, `setNumDirs`, and `setNumFiles` adjust counters by delta to emulate gauge-like values. `addRatisEvent` maintains a bounded synchronized `LinkedList`, and `getRatisEvents` exposes it as a newline-separated metric string. `unRegister` unregisters checkpoint, snapshot directory, and OM metric sources.

## Control flow
Construction creates `DBCheckpointMetrics` and stores `maxRatisEvents`. Registration is external through metrics2. Operational code elsewhere in OM calls increment methods on request start/failure/success paths. The methods themselves do not branch heavily; they increment metrics and sometimes category counters. Snapshot directory metrics are lazily created and then started. Ratis event insertion synchronizes on the list, removes the oldest event when the configured limit is reached, and appends a timestamped event string.

## State and persistence behavior
Metrics are in-memory process state, exported through Hadoop metrics/JMX sinks. They are not persisted by this class. Object-count counters can be initialized or corrected through set methods, but because they are counters used as gauges by delta adjustment, bad deltas can skew exported values. The Ratis event list is also in-memory and bounded by `maxRatisEvents`.

## Dependencies and integration points
The class integrates with Hadoop metrics2 (`DefaultMetricsSystem`, `MetricsSystem`, annotations, mutable counters/gauges), OM configuration keys for Ratis event retention, `DBCheckpointMetrics` used by checkpoint servlets, `OMSnapshotDirectoryMetrics` for periodic snapshot directory statistics, and `OmMetadataReaderMetrics` for read/list/get status counters shared with metadata-reader code paths.

## Risks and edge cases
Two methods appear suspicious from code reading: `decNumS3Buckets` increments `numS3Buckets` instead of decrementing it, and `setNumFiles` reads and updates `numDirs` instead of `numFiles`. If intentional, comments are absent; if not, these are metric correctness bugs. Counter fields are initialized by metrics2 injection during registration, so directly constructing `OMMetrics` in tests without registration may leave annotated counters null unless metrics2 initializes them. The class uses counters for values that can decrement; negative increments are supported by `MutableCounterLong` calls here but may be surprising for metrics consumers. Many getters are `@VisibleForTesting`, so test coverage is the primary guard against copy/paste counter wiring mistakes.

## Test signals
Tests should verify category and specific counters increment together for volume, bucket, key, FS, and tenant operations; failure counters do not incorrectly increment success categories unless intended; object count setters adjust the intended metric; `decNumS3Buckets` and `setNumFiles` behavior; Ratis event bounding and timestamp formatting; snapshot directory metrics start/stop/unregister lifecycle; DB checkpoint metrics exposure; and `unRegister` removing all registered sources cleanly.
