# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_shutdown.c

Defines clean and fast shutdown management pipelines. `ftl_mngt_call_dev_shutdown()` selects `desc_fast_shutdown` when `dev->conf.fast_shutdown` is set, otherwise full `desc_shutdown`.

Full shutdown:
- Deinitializes IO path and stops core poller.
- Persists L2P, trims L2P, persists metadata, marks superblock clean, dumps stats.
- Deinitializes L2P/P2L checkpointing and rolls back device startup resources.
- Uses `ftl_mngt_rollback_device` as an error handler.

Fast shutdown:
- Stops IO path and poller.
- Persists only fast metadata state, marks SHM clean, keeps SHM-backed metadata for fast restart.
- Skips full L2P and full metadata persistence.

Risk:
- Correctness depends on the fast-shutdown shared-memory state being invalidated when metadata SHM setup fails elsewhere.
