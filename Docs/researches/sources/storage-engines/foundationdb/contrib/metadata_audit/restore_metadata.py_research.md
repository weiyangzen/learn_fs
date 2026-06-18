# sources/storage-engines/foundationdb/contrib/metadata_audit/restore_metadata.py

## Purpose
This script restores FoundationDB metadata JSON backups created by the companion backup tool. It is framed as a rollback/safety-net tool for repair operations, not disaster recovery, because `serverKeys` restoration can destabilize live storage servers and cannot restore to clusters with different server UIDs.

## Important APIs, Types, And Functions
`restore_entries(db, entries, name, prefix, end, dry_run=False, batch_size=100)` validates each hex key is inside the expected metadata range and writes batches. `clear_range(db, prefix, end, name, dry_run=False)` removes current metadata before restore. `verify_backup(args, manifest, db)` loads JSON files, validates entry shape and hex encoding, and spot-checks samples against current FDB. `main` manages CLI flags, manifest loading, confirmation, target selection, MoveKeysLock lifecycle, clear-and-restore flow, and summary.

## Control Flow
`main` requires `--backup-dir` and expects `backup_manifest.json`. `--verify` exits through the verification path. Real restore requires `--yes-i-am-sure`; `--dry-run` previews without writes. The target list is either one of `serverList`, `keyServers`, `serverKeys` or all three. Non-dry-run mode takes MoveKeysLock and disables DD. For each target, it loads `<name>.json`, computes the allowed prefix/end, clears the existing range, validates all backup keys, and writes all entries in batches.

## State And Persistence Behavior
Dry-run and verify modes read only. Restore mode clears and rewrites FDB system-key ranges under `\xff/serverList/`, `\xff/keyServers/`, and/or `\xff/serverKeys/`. It also writes DD mode and MoveKeysLock keys through the shared utility module. The script restores entry bytes exactly from hex JSON after range validation.

## Dependencies And Integration Points
It depends on `fdb`, JSON backup files, `argparse`, `os`, `sys`, and `fdb_metadata_utils`. It integrates with backup manifest counts and with FDB internal metadata layouts. The long module docstring documents operational constraints and known serverKeys privatization behavior.

## Risks And Edge Cases
The workflow intentionally overwrites current metadata. `clear_range` happens before `restore_entries`; if validation fails after clearing, that metadata type can be skipped after data has already been removed in real mode. The script takes MoveKeysLock even for `serverList`-only restore, although the strict requirement is emphasized for `serverKeys/keyServers`. Spot-check verification samples at most 20 entries and is not a full equality check. ServerKeys restore can destabilize clusters or fail for dead/different server UIDs.

## Test Signals
Unit tests should cover manifest absence, JSON/hex validation, out-of-range key rejection, dry-run no-write behavior, and target prefix selection. Integration tests in disposable clusters should verify verify-mode output, restore-only `serverList`, dry-run all-target restore, lock release after exceptions, and failure behavior when restore data contains an out-of-range key.
