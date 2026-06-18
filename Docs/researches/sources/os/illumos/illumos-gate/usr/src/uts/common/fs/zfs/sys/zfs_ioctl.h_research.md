# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ioctl.h

Defines user/kernel ioctl ABI structures, send-stream record formats, feature flags, injection records, sharing state, case-sensitivity modes, and kernel-side ZFS device soft-state helpers.

Key elements:
- Comments require 32-bit and 64-bit layout compatibility, avoiding `long` and adding explicit padding.
- Send stream fields include header type, feature flags, magic, stream flags, replay record union, and payload-size helpers.
- Backup features include dedup, dedupprops, SA spill, embedded data, LZ4, large blocks, resumable, compressed, large dnode, raw, and holds.
- `dmu_replay_record_t` defines BEGIN, OBJECT, FREEOBJECTS, WRITE, FREE, END, WRITE_BYREF, SPILL, WRITE_EMBEDDED, and OBJECT_RANGE layouts.
- `zfs_cmd_t` is the broad ioctl command carrier with nvlist pointers/sizes, legacy fields, replay begin record, inject record, stat data, and send/receive fields.
- `zinject_record_t` and `zinject_type_t` define fault-injection control data.

Main dependencies and interactions:
- Depends on credentials, DMU, ZIO, delegation, SPA, and `zfs_stat.h`.
- Consumed by userland `zfs`/`zpool` tools and kernel ioctl handlers.
- Kernel-only declarations include security policy helpers, `getzfsvfs`, minor allocation, soft-state lookup, and control-device/zvol type selection.

Implementation notes:
- This is a high-risk ABI header: record ordering, field sizes, padding, and feature masks must remain compatible.
- `DMU_STREAM_SUPPORTED()` rejects unknown feature bits outside `DMU_BACKUP_FEATURE_MASK`.
