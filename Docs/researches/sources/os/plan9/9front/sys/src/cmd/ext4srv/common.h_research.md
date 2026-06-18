# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/common.h

This header defines shared ext4srv option and partition structures plus lifecycle prototypes.

Key structures:
- `Opts`: mount/open options including group, as-root mode, ream flag, block size, inode size, and label.
- `Part`: reference-counted, locked mounted partition object. It links into a list, stores the device path, ext4 mountpoint/blockdev/interface/superblock/locks, Plan 9 qid fields, group data, backing fd, and trailing block buffer.

Key functions declared:
- `openpart`
- `closepart`
- `closeallparts`
- `statallparts`
- `syncallparts`

Important implementation notes:
- `Part` embeds both Plan 9 synchronization/reference primitives (`Ref`, `QLock`) and ext4 library structures.
- The flexible `blkbuf[]` tail indicates allocation size depends on block-buffer needs.
