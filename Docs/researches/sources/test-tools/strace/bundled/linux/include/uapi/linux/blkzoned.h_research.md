<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/blkzoned.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/blkzoned.h

Purpose: UAPI for zoned block device reporting and zone management ioctls.

Important APIs/types: enums `blk_zone_type`, `blk_zone_cond`, and `blk_zone_report_flags`; `struct blk_zone` 64-byte descriptor; `struct blk_zone_report` with flexible `zones[]`; `struct blk_zone_range`; ioctl constants `BLKREPORTZONE`, `BLKREPORTZONEV2`, `BLKRESETZONE`, `BLKGETZONESZ`, `BLKGETNRZONES`, `BLKOPENZONE`, `BLKCLOSEZONE`, and `BLKFINISHZONE`.

Control flow: declarative ABI. Comments specify 512-byte sector units, cached report behavior, deprecated `BLKREPORTZONE`, and zone alignment requirements.

State and persistence: real ioctls read or mutate zone write pointer/state on block devices; header itself defines structs/constants only.

Dependencies and integration: includes `<linux/types.h>` and `<linux/ioctl.h>`, used by strace ioctl decoders.

Risks: flexible array reports require bounds checking from `nr_zones`. New Linux 6.19 cached/active flags can be unknown to older decoders. Test signals: decoder tests should cover report v1/v2 flags, range ioctls, and active/cached enum values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/blkzoned.h -->
