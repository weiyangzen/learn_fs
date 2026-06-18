# File Research: sources/os/linux/linux/fs/xfs/xfs_rmap_item.c

## Role

Deferred log intent/done item implementation for reverse mapping btree updates. It makes rmap updates crash-recoverable across rolled transactions for both data and realtime metadata.

## Main Responsibilities

- Defines caches for RUI/RUD log items: `xfs_rui_cache`, `xfs_rud_cache`.
- Manages RUI lifecycle: allocation, formatting, unpin, release, AIL deletion, dynamic freeing.
- Manages RUD lifecycle and links done items back to original RUI intents.
- Encodes rmap operation details into `xfs_map_extent` fields in `xfs_rmap_update_log_item`.
- Adds deferred rmap work via `xfs_rmap_defer_add`, splitting realtime and data-section work into distinct defer types.
- Finishes deferred work through `xfs_rmap_finish_one`.
- Recovers RUIs by validating map records, rebuilding `xfs_rmap_intent` entries, allocating recovery transactions, and committing/capturing deferred work.
- Relogs old intent items to move the log tail.
- Provides recovery handlers for RUI/RUD and realtime RUI/RUD log records.

## Supported Rmap Intent Types

Map, map shared, unmap, unmap shared, convert, convert shared, alloc, and free. Flags also preserve unwritten state and attr-fork state.

## Consistency Checks

Recovery rejects RUIs if rmapbt is unavailable, flags are invalid, operation type is unknown, inode owners fail verification, file offsets are invalid, or data/realtime physical extents are invalid.

## Realtime Handling

Realtime rmap intents use `XFS_LI_RUI_RT` and `XFS_LI_RUD_RT`, and separate defer ops named `rtrmap`. If realtime support is disabled, recovered realtime intents are flagged as corruption.

## Dependencies

Uses defer ops, transaction/log recovery internals, rmap btree helpers, AG/RT group intent references, btree cursor cleanup, and tracepoints.
