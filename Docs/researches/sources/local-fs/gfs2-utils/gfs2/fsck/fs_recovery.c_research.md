# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.c

## Purpose
Implements GFS2 journal validation, replay, clearing, and journal-index discovery/rebuild support for `fsck.gfs2`.

## Main Elements
- Revoke tracking: `revoke_add()`, `revoke_check()`, `revoke_clean()` maintain replay-time revoke state.
- Replay scanners:
  - `revoke_lo_scan_elements()` collects revokes in pass 0.
  - `buf_lo_scan_elements()` replays metadata blocks in pass 1.
  - `databuf_lo_scan_elements()` replays journaled data blocks and unescapes magic.
  - `foreach_descriptor()` walks active log descriptors between head tail and head block.
- Journal repair:
  - `check_journal_seq_no()` detects and optionally renumbers out-of-order log header sequences.
  - `recover_journal()` checks head, handles corrupt/dirty/clean states, gates preen safety, prompts, replays, cleans, or clears journals.
- Safety: `preen_is_safe()` prevents automatic preen on cluster locking unless forced or lock_nolock.
- Journal validation: range-check metawalk callbacks ensure journal inode pointers are in range and point to indirect blocks.
- Public orchestration:
  - `replay_journals()` checks each journal inode, replays or reports, counts clean journals, and fsyncs.
  - `ji_update()` reads `journalN` inodes from `jindex`.
  - `build_jindex()` recreates the journal index and journals.
  - `init_jindex()` validates/rebuilds `jindex`, checks entry names, and populates journal info.

## Dependencies And Integration
Used during fsck initialization/recovery before normal passes. Integrates libgfs2 journal helpers, metawalk validation, logging, user queries, resource group refresh, and fsck options.

## Risk Notes
Journal replay writes metadata and journaled data to the filesystem. Preen safety is conservative for clustered filesystems, but forced/manual modes can still clear or replay journals based on user confirmation.
