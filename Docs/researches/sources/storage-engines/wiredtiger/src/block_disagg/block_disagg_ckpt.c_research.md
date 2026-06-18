# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_ckpt.c

## Purpose
Implements checkpoint integration for the disaggregated block manager. It turns a checkpoint root page into a page-log object, packs that root page's disaggregated address as the checkpoint cookie stored in metadata, resolves shared-table metadata after successful checkpoints, and unpacks checkpoint cookies during checkpoint load.

## Important APIs, types, and functions
- `__wti_block_disagg_checkpoint` is the `WT_BM::checkpoint` implementation. It iterates checkpoint entries and fills newly added checkpoints.
- `__bmd_checkpoint_pack_raw` writes the root image with `__wti_block_disagg_write_internal`, packs a `WT_BLOCK_DISAGG_ADDRESS_COOKIE`, updates root-size accounting, and sets `WT_CKPT::size`.
- `__wti_block_disagg_checkpoint_resolve` wraps `__block_disagg_checkpoint_resolve` in the schema lock.
- `__block_disagg_checkpoint_resolve` updates shared/disaggregated metadata after a successful checkpoint.
- `__wti_block_disagg_checkpoint_load` unpacks a checkpoint cookie and repacks it as the root page address cookie.
- Important structures are `WT_BLOCK_DISAGG`, `WT_CKPT`, `WT_PAGE_BLOCK_META`, `WT_BLOCK_DISAGG_ADDRESS_COOKIE`, and connection-level `disaggregated_storage` metadata.

## Control flow
Checkpoint creation enters through the block-manager vtable. For every `WT_CKPT_ADD` checkpoint, `__bmd_checkpoint_pack_raw` either records an empty raw checkpoint when no root image exists or byteswaps the root page header, writes the page to the page log, restores the page header, and packs a cookie containing `page_id`, `disagg_lsn`, `base_lsn`, encoded size, and checksum. Root size is then applied to the live disaggregated block size and copied into `ckpt->size`.

Checkpoint resolve is separate from writing the root page. With the schema lock held, it skips failed checkpoints. For the shared metadata table it reads the local metadata entry, optionally persists updated key-encryption information, extracts the checkpoint config, and writes checkpoint metadata with timestamp and schema epoch. For ordinary shared tables it derives a table/layered name from the file name and enqueues a `WT_SHARED_METADATA_UPDATE` operation for the current schema epoch.

Checkpoint load is intentionally address-oriented: it does not fetch the root page itself. It unpacks the raw checkpoint cookie, records the current root size on the block handle, then packs the same cookie into the caller's `root_addr` buffer so the normal page read path can fetch the root.

## State and persistence behavior
The checkpoint cookie is the disaggregated page address for the root page. This coupling is explicitly relied on when old checkpoint root pages are discarded. `ckpt->size` is taken from `block_disagg->size` after root-size transition accounting, so metadata uses the same size view as live block accounting. Resolve writes checkpoint metadata into either system metadata for the shared metadata file or the shared metadata operation queue for ordinary stable/shared tables. `current_root_size`, `previous_root_size`, and checkpoint generation handling live in `block_disagg_size.c` but are driven here.

## Dependencies and integration points
This file depends on the page-log write path in `block_disagg_write.c`, checkpoint/address pack helpers, metadata cursors, the disaggregated metadata queue, key-provider crypt helper, and the schema lock. It is installed as `WT_BM::checkpoint`, `checkpoint_load`, and `checkpoint_resolve` in `block_disagg_mgr.c`.

## Risks and edge cases
- The root checkpoint cookie and address cookie are assumed identical; changing either format requires coordinated discard/checkpoint changes.
- Root-page byteswapping is done in place and restored after the write. Any early-return path around that operation must preserve restoration.
- `__bmd_checkpoint_pack_raw` panics on root-page write failure, making page-log availability a hard checkpoint requirement.
- File-name suffix stripping for `.wt` and `.wt_stable` is convention-sensitive and also supports suffix-less test files.
- Checkpoint size correctness depends on root-size adjustment happening before metadata persistence and rollback logic reversing failed generations.

## Test signals
Useful tests include successful and failed disaggregated checkpoints, empty root checkpoints, checkpoint load of packed root cookies, metadata resolve for both `WT_DISAGG_METADATA_FILE` and ordinary shared tables, key-provider metadata propagation, checkpoint failure rollback size checks, and recovery/open paths that verify `ckpt->size` matches disaggregated block size.
