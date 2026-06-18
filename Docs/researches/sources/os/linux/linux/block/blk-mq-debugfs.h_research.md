# File Research: sources/os/linux/linux/block/blk-mq-debugfs.h

## Summary
Declares blk-mq debugfs attribute structures and registration functions, with no-op fallbacks when debugfs support is disabled.

## Main Contents
- `struct blk_mq_debugfs_attr`, containing name, mode, show callback, write callback, and optional seq operations.
- Request display helpers.
- Queue, hctx, scheduler, scheduler-hctx, and rq-qos debugfs registration functions.
- `queue_zone_wplugs_show()` declaration or no-op fallback.

## Important Behavior
When `CONFIG_BLK_DEBUG_FS` is disabled, all registration functions compile to empty inline functions. Zoned write plug debug display is available only with both zoned block device and block debugfs support.

## Risks
Code using these helpers must not depend on debugfs side effects. Attribute definitions must set either `.show` or `.seq_ops` consistently because the implementation treats seq-only attributes as read-only.
