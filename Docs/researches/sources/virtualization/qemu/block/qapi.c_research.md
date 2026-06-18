# File Research: sources/virtualization/qemu/block/qapi.c

## Purpose
Implements block-layer QAPI query and human-readable dump helpers. It builds QMP response objects for block devices, block nodes, block graphs, image metadata, snapshots, block statistics, latency histograms, and format-specific information.

## Main Entry Points
- `bdrv_block_device_info()` builds `BlockDeviceInfo` for an inserted backend/node.
- `bdrv_query_snapshot_info_list()` converts internal snapshot records into QAPI `SnapshotInfoList`.
- `bdrv_query_image_info()` recursively builds `ImageInfo` for an image/backing chain.
- `bdrv_query_block_graph_info()` recursively builds full graph information including children.
- `qmp_query_block()` implements the QMP query for visible block backends.
- `qmp_query_blockstats()` reports either backend-level stats or node-level stats.
- `bdrv_snapshot_dump()`, `bdrv_image_info_specific_dump()`, and `bdrv_node_info_dump()` print human-readable monitor/qemu-img-style output.

## Internal Mechanics
`bdrv_block_device_info()` refreshes filenames, records read-only/driver/cache/encryption/active state, child node references, backing filename, dirty bitmaps, detect-zeroes, throttle settings, write threshold, and image metadata. It skips implicit filters for backend-level compatibility where appropriate.

`bdrv_do_query_node_info()` is the common node metadata builder. It reads length, allocated size, cluster size, dirty flag, block limits, format-specific info, backing filenames, and snapshot lists. Image and graph queries layer recursion on top of this base.

Stats collection splits backend accounting (`bdrv_query_blk_stats()`) from recursive node stats (`bdrv_query_bds_stats()`). Backend stats include byte/op counts, failed/invalid operations, merged counts, total latencies, idle time, timed interval stats, queue depth, and latency histograms. Node stats include node name, highest write offset, driver-specific stats, primary/data child recursion, and legacy backing recursion for backend-level queries.

Dump helpers convert QAPI objects through QObject visitors and recursively print dictionaries/lists with indentation. Node-info dumping prints image/protocol names, virtual/file length, disk size, encryption, cluster size, dirty shutdown status, backing details, block limits, snapshots, and format-specific data.

## Dependencies
Uses QAPI block-core types and visitors, QObject/QDict/QList/QNum/QBool helpers, QEMU printing utilities, block dirty bitmap queries, throttle-group APIs, write-threshold support, block accounting, and `BlockBackend` traversal.

## Filesystem/Block Relevance
This file is the reporting surface for QEMU block storage. It determines what management tools see for image topology, backing chains, allocation details, limits, snapshots, dirty bitmaps, and performance counters.

## Risks and Notes
- Backend-level queries intentionally skip implicit filters, while node-level queries stay at exact nodes.
- Recursive graph and image queries must free partially built QAPI objects on error.
- Snapshot listing treats unsupported or no-medium as recoverable for node info, but propagates other errors.
- Human-readable dumping depends on QObject conversion of QAPI structs and assumes only supported QObject types are produced.
