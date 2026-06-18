# sources/sync-backup/borg/src/borg/testsuite/legacy_helpers_test.py

Purpose: tests helper predicates used to interpret Borg 1.x hardlink metadata during migration.

Important APIs and control flow: helper `_item` builds an `Item` with mode/path/mtime and optional legacy fields. Tests verify `borg1_hardlinkable` returns true for regular files, block devices, character devices, and FIFOs, and false for symlinks, directories, and sockets. `borg1_hardlink_master` requires a truthy `hardlink_master` flag. `borg1_hardlink_slave` requires a `source` and a hardlinkable mode, including non-regular hardlinkable types.

State and persistence: in-memory `Item` metadata only.

Dependencies and integration points: depends on `stat`, `Item`, and `borg.legacy.helpers`. These predicates feed `UpgraderFrom12To20` hardlink handling.

Risks: hardlinkability differs from normal-file-only assumptions; FIFOs and device nodes are included for Borg 1 compatibility. Symlink source means target in modern metadata, so mode matters.

Test signals: boolean predicate results for each file type and legacy field combination.
