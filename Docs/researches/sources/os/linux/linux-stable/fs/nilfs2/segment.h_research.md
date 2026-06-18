# File Research: sources/os/linux/linux-stable/fs/nilfs2/segment.h

`segment.h` declares recovery state and segment-constructor state. `struct nilfs_recovery_info` stores whether recovery is needed, last super-root block/checkpoint, roll-forward bounds and sequence, used segment list, last partial segment location, sequence, current segment number, and next segment number. Recovery flags distinguish super-root update detection from completed roll-forward.

`struct nilfs_cstage` stores collection stage count, flags, and cursor pointers for dirty-file and GC-inode iteration. `struct nilfs_sc_info` is the full segment-constructor object: superblock/root, block increments, dirty/GC/iput lists, freeseg array, dsync target/range, segment-buffer lists, current segment, summary-entry cursors, block counters, checkpoint/time fields, internal flags, request state, wait queues, request sequence counters, sync flag, timing/watermark settings, timer, and thread pointer.

Constructor flags track dirty metadata, unclosed logical segments, whether the latest segment has a super root, prior flush pressure, and whether a checkpoint has changes beyond core metadata/GC movement. State includes `NILFS_SEGCTOR_COMMIT`.

The header declares default timeout, super-root frequency, watermark, cleanup retry count, and external APIs implemented in `segment.c` and `recovery.c`: construction, dsync construction, GC cleaning, log-writer attach/detach, super-root reading/searching, orphan-log salvage, and segment-list disposal.

This header is the state contract between mount/recovery/superblock code and the segment writer.
