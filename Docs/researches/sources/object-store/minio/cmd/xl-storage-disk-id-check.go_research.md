# sources/object-store/minio/cmd/xl-storage-disk-id-check.go

Wraps `xlStorage` with disk-ID validation, deadlines, health monitoring, metrics, and storage tracing. It detects swapped/stale disks by comparing cached disk ID with the ID read from `format.json`, rejects mismatches as `errDiskNotFound`, and marks unhealthy disks offline until write/read/delete probes succeed.

Key types are `storageMetric`, `xlStorageDiskIDCheck`, `lockedLastMinuteLatency`, and `diskHealthTracker`. Most storage methods call `TrackDiskHealth`, delegate to `xlStorage`, enforce `globalDriveConfig` deadlines, update write/delete counters where relevant, and emit per-operation metrics/traces. `monitorDiskWritable` periodically writes and reads a sentinel buffer in `minioMetaTmpBucket`; `monitorDiskStatus` brings a drive back online after a successful write/read/delete loop. `diskHealthReader` and `diskHealthWriter` update success timestamps from low-level I/O.

Persistent effects include temp healthcheck objects and storage write/delete attributes. Risks include false offline decisions under slow disks, stale disk-ID reads, waiting counter imbalance, recursive tracking gaps, temp-object cleanup failure, and `ReadParts` assuming a non-empty path slice. No direct tests in this subset cover these behaviors.
