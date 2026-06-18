# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devname.c

Purpose: resolves device names, probes block devices, and populates the blkid cache from system enumeration sources.

Important APIs and control flow: `blkid_get_dev(cache, devname, flags)` finds or creates a cache entry and optionally verifies it with `blkid_verify`; verified entries trigger stale duplicate cleanup by matching type/label/UUID. `probe_one()` resolves a `/proc/partitions` name and `dev_t` to a path using `/dev`, `/devfs`, `/devices`, `/dev/mapper`, sysfs DM names, or exhaustive `blkid_devno_to_devname`, then probes with `BLKID_DEV_NORMAL` and assigns priority. `probe_all()` rate-limits using `BLKID_PROBE_INTERVAL`, reads cache, scans EVMS and old LVM `/proc` hierarchies, parses `/proc/partitions`, skips extended partitions, removes whole-disk cache entries when partitions exist, probes remaining devices, and flushes the cache. `blkid_probe_all` and `blkid_probe_all_new` expose full and new-only scans.

State and persistence: mutates device entries, priorities, verification flags, cache probed time, and on-disk cache via flush.

Dependencies and integration: integrates with `probe.c`, `devno.c`, `cache.c`, `/proc`, `/sys`, and device nodes.

Risks and test signals: old kernel/proc heuristics, real-device side effects, fixed path buffers, and stale duplicate removal are risky. Test with loop devices, DM leaf/non-leaf maps, LVM/EVMS absence, partitioned disks, new-only scans, and unreadable devices.
