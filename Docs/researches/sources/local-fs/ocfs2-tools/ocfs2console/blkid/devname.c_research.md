# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devname.c

Finds, creates, verifies, and bulk-probes blkid device entries by device name.

Key functions:
- `blkid_get_dev(cache, devname, flags)`
  - Finds cached device by path.
  - Optionally creates a cache entry.
  - Optionally verifies it against disk via `blkid_verify`.
- `probe_one(cache, ptname, devno, pri)`
  - Resolves a `/proc` partition name to a real device path.
  - Reuses existing cached entries by `dev_t`.
  - Falls back to `blkid_devno_to_devname`.
  - Assigns device priority, including MD default priority.
- `lvm_get_devno`, `lvm_probe_all`
  - Walk old `/proc/lvm/VGs/.../LVs` hierarchy and probe logical volumes.
- `evms_probe_all`
  - Reads `/proc/evms/volumes` and probes EVMS devices.
- `blkid_probe_all(cache)`
  - Refreshes cache from disk.
  - Probes EVMS, LVM, and `/proc/partitions`.
  - Skips most whole disks when partition devices are present.
  - Flushes cache after probing.

Dependencies:
- `/proc/partitions`
- `/proc/lvm/VGs`
- `/proc/evms/volumes`
- `blkid_verify` from `probe.c`
- `blkid_devno_to_devname` from `devno.c`

Notable details:
- Whole-disk versus partition detection is heuristic: partition names ending in digits are treated as partitions.
- Extended partitions are skipped by size check `sz > 1`.
- Cache probing is throttled using `BLKID_BIC_FL_PROBED` and `BLKID_PROBE_INTERVAL`.
