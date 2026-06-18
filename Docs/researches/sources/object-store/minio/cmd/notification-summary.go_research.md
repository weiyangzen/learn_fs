# sources/object-store/minio/cmd/notification-summary.go

This small file provides capacity aggregation helpers used by metrics and notification/admin summaries. It computes raw and usable total/free capacity from `madmin.Disk` slices and object-layer storage backend parity information.

The APIs are `GetTotalCapacity`, `GetTotalUsableCapacity`, `GetTotalCapacityFree`, and `GetTotalUsableCapacityFree`. Raw helpers simply sum `TotalSpace` or `AvailableSpace` for all disks. Usable helpers skip disks with invalid pool indexes or pool indexes outside `StorageInfo.Backend.StandardSCData`, then exclude parity disks by comparing `disk.DiskIndex` with the pool's standard storage class data count. Only data disks contribute to usable capacity.

State is read-only input data with no persistence. Integration points include legacy `storageMetricsPrometheus`, cluster health metrics, `NotificationSys.StorageInfo`, and admin/server info paths that need aggregate capacity. The code depends on `madmin-go` disk structs and the MinIO `StorageInfo` alias defined in object API data types.

Risks: usable capacity depends on correct `PoolIndex`, `DiskIndex`, and `StandardSCData` values. Invalid indexes are silently skipped to avoid crashes, following a referenced historical issue. This can under-report capacity if backend metadata is incomplete. There are no direct tests in this file; test signal is integration-level through storage metrics and admin info behavior.
