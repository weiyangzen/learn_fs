# sources/test-tools/stress-ng/stress-rawdev.c research

Purpose: implements `rawdev`, a root-only I/O stressor that opens the raw block device backing the temp path and reads it with direct I/O using several access patterns.

Important APIs, types, and functions: `stress_rawdev_func` abstracts read methods. Method table entries include all, sweep, wiggle, ends, random, and burst. Each method uses `pread()` into an aligned mmap buffer and accumulates byte/duration metrics. `stress_rawdev_all()` rotates through all concrete methods and aggregates metrics.

Control flow: `stress_rawdev()` requires euid root, finds the mount device for the stress temp path, opens it, queries block count and sector size via `BLKGETSIZE` and `BLKSSZGET`, clamps block size, maps an aligned buffer, reopens with `O_DIRECT`, synchronizes, and repeatedly calls the selected access method. On exit it emits per-method MB/sec metrics, unmaps, closes, and frees metrics.

State and persistence: only transient file descriptors, buffer mapping, and metrics are used. Reads are non-mutating, so no persistent device changes are intended.

Dependencies and integration: gated by `sys/sysmacros.h`, block ioctls, and root. Uses stress-ng mount-device lookup, mmap, vmstat/metrics helpers, and option method parsing. Classified as `CLASS_IO`, `VERIFY_ALWAYS`.

Risks: reading raw devices can be disruptive on physical disks due to seek-heavy patterns and needs root. Device discovery may fail in containerized or non-block-backed temp paths. `O_DIRECT` alignment depends on mmap/page sizing and clamped block size.

Test signals: root skip, mount-device discovery skip, ioctl skip, selected method progress, per-method MB/sec metrics, and `pread` failure logs.
