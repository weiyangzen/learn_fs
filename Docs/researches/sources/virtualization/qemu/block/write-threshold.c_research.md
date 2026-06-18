# File Research: sources/virtualization/qemu/block/write-threshold.c

Small block-core helper for write-threshold notifications. It stores a threshold in `BlockDriverState` and emits a QAPI event when a write crosses it.

Key responsibilities:
- Get and set `bs->write_threshold_offset`.
- Implement QMP command `block-set-write-threshold` by looking up a node name and storing the threshold.
- Check writes via `bdrv_write_threshold_check_write()` and send `BLOCK_WRITE_THRESHOLD` with excess bytes and threshold value.
- Auto-disable the threshold after the first event to avoid monitor flooding.

Important functions:
- `bdrv_write_threshold_get()`
- `bdrv_write_threshold_set()`
- `qmp_block_set_write_threshold()`
- `bdrv_write_threshold_check_write()`

Notable constraints:
- Threshold comparison uses write end offset, `offset + bytes`.
- A zero threshold disables notifications.
- Missing nodes are reported through `Error **errp`.
