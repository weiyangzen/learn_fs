# File Research: sources/virtualization/spdk/module/bdev/ocf/stats.h

This header declares the OCF statistics adapter. `struct vbdev_ocf_stats` groups OCF usage, request, block, and error statistic structs into one container for collection and JSON formatting.

The exported functions get stats for a named core, reset stats for a named core, and write a stats object to a SPDK JSON writer. It is used by OCF RPC or management code to present OCF counters through SPDK interfaces.
