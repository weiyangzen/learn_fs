# sources/storage-engines/wiredtiger/test/suite/test_export01.py

## Purpose

Tests basic `backup:export` behavior: creation/removal of `WiredTiger.export`, propagation into a copied home, and correctness after restarting from an exported backup.

## Important APIs, Types, and Functions

Defines `test_export01` using `TieredConfigMixin`, `copy_wiredtiger_home`, `gen_tiered_storage_sources`, `make_scenarios`, `os`, and `shutil`. Main tests are `test_export` and `test_export_restart`.

## Control Flow

`test_export` creates three tables, inserts rows, checkpoints, opens `backup:export`, copies the home, asserts `WiredTiger.export` exists while cursor is open, closes cursor, and verifies the file is removed from home but retained in backup. `test_export_restart` copies an export backup, reopens it, creates a new table, drops an old table, opens export again, and inspects file contents.

## State and Persistence Behavior

Persistence spans home copying, backup cursor lifetime, restart into a backup directory, and export metadata updates after create/drop. Tiered scenarios flush tiers where applicable; restart is skipped for tiered.

## Dependencies and Integration Points

Depends on helper copy logic, WiredTiger backup cursor integration, filesystem operations, checkpoints, and tiered storage hooks.

## Risks and Maintenance Signals

The content check only searches for table-name substrings. Backup-copy fidelity and export file generation are sensitive to cursor lifetime and tiered flush timing.

## Test Signals

Signals are export file existence/removal, backup copy retention, restart usability, and `exportc` present while dropped `exportb` is absent.
