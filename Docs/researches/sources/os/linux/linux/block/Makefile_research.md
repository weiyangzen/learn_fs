# File Research: sources/os/linux/linux/block/Makefile

This Makefile assembles the Linux block-layer core and conditional subfeatures.

Always-built objects include core block-device lifetime and I/O infrastructure: `bdev.o`, `fops.o`, `bio.o`, `elevator.o`, `blk-core.o`, `blk-sysfs.o`, flush/settings/ioc/map/merge/timeout/lib/mq/tag/dma/stat/sysfs/cpumap/sched support, `ioctl.o`, `genhd.o`, `ioprio.o`, `badblocks.o`, `partitions/`, `blk-rq-qos.o`, `disk-events.o`, `blk-ia-ranges.o`, and `early-lookup.o`.

Conditional build links:
- BSG: `bsg.o`, `bsg-lib.o`.
- blk-cgroup controllers: `blk-cgroup.o`, `blk-cgroup-rwstat.o`, `blk-cgroup-fc-appid.o`, `blk-throttle.o`, `blk-ioprio.o`, `blk-iolatency.o`, `blk-iocost.o`.
- schedulers: `mq-deadline.o`, `kyber-iosched.o`, and composite `bfq.o` built from `bfq-iosched.o bfq-wf2q.o bfq-cgroup.o`.
- integrity: `bio-integrity.o`, `blk-integrity.o`, `t10-pi.o`, `bio-integrity-auto.o`, `bio-integrity-fs.o`.
- zoned, writeback throttling, debugfs, Opal SED, power management, blk-crypto, crypto fallback, and deprecated holder support.

This file establishes that `badblocks.c` and `bdev.c` are core block-layer code, while BFQ and bio-integrity helpers are feature-gated.
