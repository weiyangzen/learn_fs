# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_p2l.c

Management helpers for P2L checkpoint and P2L IO log metadata.

Functions:
- Initialize/deinitialize checkpoint objects.
- Wipe all P2L checkpoint regions.
- Conditionally wipe P2L IO log regions only if those layout regions have allocated blocks.
- Free checkpoint metadata buffers after use.
- Restore all checkpoint metadata regions unless fast startup can skip disk restore.

The wipe implementation iterates metadata regions sequentially with `ftl_md_clear`. Restore dispatches `ftl_md_restore` to all checkpoint regions and tracks aggregate completion/status in step context.

Role: prepares and restores the metadata regions used by `ftl_p2l.c` and P2L IO log recovery, keeping these operations in the management step model.
