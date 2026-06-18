# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_startup.c

Defines FTL startup, first-create startup, clean restore, dirty recovery selection, RPC trim, and rollback orchestration.

Main startup path:
- `ftl_mngt_call_dev_startup()` executes `desc_startup`.
- Common steps validate config, open base/cache bdevs, initialize superblock, pools, bands, IO device/channel, layout, upgrades, metadata, NV cache, valid/trim maps, band metadata, reloc, then choose create or restore mode.
- Create mode clears L2P, initializes bands, persists initial band/chunk metadata, wipes P2L regions, clears trim metadata/log, marks dirty, starts poller, and finalizes.
- Restore mode chooses clean startup if `dev->sb->clean`, otherwise calls dirty recovery.

Trim path:
- `ftl_mngt_trim()` allocates context and runs a one-step management process calling `spdk_ftl_unmap()`.
- User callback is marshaled back to the original thread.

Risk:
- `ftl_mngt_process_trim_cb()` calls `ftl_mngt_fail_step(ctx)` with `ctx` typed as `void *`; it is the same pointer as `mngt`, but the local variable should be used for clarity.
