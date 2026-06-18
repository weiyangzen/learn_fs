# sources/sync-backup/borg/src/borg/legacy/helpers.py

## Purpose
Provides Borg 1.x hard-link classification helpers for legacy item conversion.

## Important APIs, Types, And Functions
`borg1_hardlinkable(mode)` returns true for regular files, block devices, character devices, and FIFOs. `borg1_hardlink_master(item)` detects old-style hard-link masters. `borg1_hardlink_slave(item)` detects old-style hard-link slaves with a `source`.

## Control Flow
The helpers inspect `stat` file type bits and selected item fields. Masters require `hardlink_master` truthy, no `source`, and a hardlinkable mode. Slaves require `source` and hardlinkable mode.

## State And Persistence
No state and no persistence.

## Dependencies And Integration Points
Used by Borg 1.x archive transfer/upgrade code to map old hard-link representation to newer hard-link identities and chunk reuse. Depends only on `stat` and item dict-like access.

## Risks And Edge Cases
Only selected file types are hardlinkable; directories and symlinks are excluded. Item field presence controls classification, so malformed legacy items can be misclassified or ignored.

## Test Signals
Existing legacy helper tests should cover each supported file type, unsupported types, master/slave field combinations, absent `hardlink_master`, and `source` interactions.
