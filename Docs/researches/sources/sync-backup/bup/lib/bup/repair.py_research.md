<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repair.py -->
# sources/sync-backup/bup/lib/bup/repair.py

## Purpose
This module records repair actions performed during `bup get --repair` or related rewrite flows and renders those actions as commit trailers.

## Important APIs, Types, And Functions
The public pieces are `valid_repair_id()` and `Repairs`. `Repairs` exposes `repair_count()`, `note_incidental_repair()`, `meta_replaced()`, `path_replaced()`, `link_blob_restored()`, `link_blob_fixed()`, and `repair_trailers()`.

## Control Flow
Each repair-recording method logs the repair id on the first repair, remembers the affected save via `_remember_save()`, and appends path/object details to a category list. `repair_trailers()` emits `Bup-Repair-ID`, repaired save refs, replaced file metadata, restored/fixed symlink blob notes, and lost metadata notes.

## State And Persistence Behavior
State is held in one `Repairs` instance: id, destructive flag, incidental count, ordered repaired-save map, and repair detail lists. Persistence happens only when callers append generated trailers to new commits.

## Dependencies And Integration Points
It depends on `vfs.Commit`, `vfs.RevList`, `render_path()`, hex encoding, shell byte quoting, and logging. `cmd/get.py` uses `valid_repair_id()` for CLI validation and repair tracking during rewrite/repair transfers.

## Risks And Edge Cases
`valid_repair_id()` allows any printable ASCII byte including spaces; trailer consumers must parse accordingly. `_remember_save()` assumes a specific VFS path shape with revlist and commit at positions 1 and 2. The `destructive` flag is stored here but not interpreted by this module.

## Test Signals
`test/ext/test-get-repair-bupm`, `test/ext/test-get-repair-symlinks`, `test/ext/test-get-rewrite-missing`, `test/ext/test-get-missing`, and get command unit/integration tests cover repair trailer generation and CLI validation paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repair.py -->
