# File Research: sources/os/plan9/9front/sys/src/cmd/disk/qcowfs.c

## Purpose
Provides a small 9P server exposing a qcow2 image as a single writable `data` file, and can create a new qcow2 v3 image.

## Key Behavior
- Defines qcow2 header fields, big-endian serialization helpers, cluster/refcount/L1/L2 constants, and a Plan 9 `ftruncate()` wrapper using `dirfwstat`.
- `qc2create()` creates a qcow2 v3 image with 64 KiB clusters, an L1 table, refcount table/block, and initial refcounts for metadata clusters.
- `qc2open()` reads and validates qcow2 v2/v3 headers, rejects unsupported refcount order, loads and byte-swaps the L1 table, and records the current file length as allocation end.
- `xlate()` maps virtual offsets to physical image offsets through L1/L2 tables, returning zero for unallocated clusters and rejecting compressed clusters.
- `mkcluster()` allocates L2 tables and data clusters, updates L1 entries, refcounts, and optionally copies data from an existing physical cluster before write.
- `fsread()` serves reads by translating each cluster; holes read as zeroes and reads are capped at virtual disk size.
- `fswrite()` rejects writes past the virtual disk size and allocates clusters for holes or non-inplace mappings before writing.
- `main()` accepts `-n size` to create, `-m mntpt`, `-s srv`, and `-D` for 9P tracing, then posts/mounts a 9P tree containing `data`.

## Interfaces And Dependencies
- Uses Plan 9 `thread` and `9p` libraries, with `Srv.read`/`Srv.write` handlers.
- Exposes only one file named `data` with length equal to qcow2 virtual disk size.
- The `Disk.base` field and `copy_cluster()` support copy-on-write shape but this program opens only one image as its own base for writes.

## Notes
Feature support is intentionally narrow: no compression, no encryption handling beyond storing the header value, no snapshots, no backing-file opening, and only 16-bit refcounts. Allocation/refcount updates are fatal on I/O failures rather than recoverable 9P errors.
