# File Research: sources/virtualization/spdk/lib/bdev/bdev_rpc.c

`bdev_rpc.c` implements core SPDK bdev JSON-RPC methods. It is control-plane code for global bdev options, examination, device inventory, I/O statistics, QoS, queue-depth sampling, and histograms.

Registered RPCs include `bdev_set_options`, `bdev_wait_for_examine`, `bdev_examine`, `bdev_get_iostat`, `bdev_reset_iostat`, `bdev_get_bdevs`, `bdev_set_qd_sampling_period`, `bdev_set_qos_limit`, `bdev_enable_histogram`, `bdev_get_histogram`, and `bdev_get_histogram_borders`.

Option setting uses an X-macro field list shared between the generated RPC context and `spdk_bdev_opts`, guarded by a static size assertion. It decodes optional pool/cache/examine/iobuf values and calls `spdk_bdev_set_opts()`.

Examination RPCs either wait for all automatic examine work to complete or trigger examination of a named bdev. Device inventory emits aliases, product name, block geometry, preferred write/unmap hints, UUID, NUMA id, metadata/DIF fields, QoS limits, claim state, zoned fields, supported I/O types, memory-domain types, and driver-specific JSON.

I/O stats handling is asynchronous and reference-counted by outstanding bdev count. It supports all bdevs, selected names, optional per-channel stats for exactly one bdev, and optional reset mode. It opens bdev descriptors, allocates stats buffers, gathers device or per-channel stats, emits JSON, closes descriptors, and frees contexts after all asynchronous callbacks complete.

Reset stats follows similar asynchronous fan-out. It can reset a single named bdev or all bdevs, supports reset mode, calls driver-specific reset hooks when present, and completes the RPC after all device stat reset callbacks return.

QoS and queue-depth RPCs open the named bdev, configure sampling period or rate limits, and return asynchronous completion for QoS. Histogram RPCs enable/disable histogram collection with optional opcode, granularity, min, and max values; readout either returns base64-encoded bucket data plus metadata or counts for requested histogram borders converted from microseconds to ticks.

Research notes: this file is careful about not beginning JSON responses until it knows asynchronous fan-out can be represented correctly. Many error paths close descriptors immediately after submitting asynchronous operations, relying on bdev references held by the operation itself.
