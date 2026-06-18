## sources/sync-backup/bup/test/ext/test-fsck

Purpose: exercises repository integrity checking, par2 generation/repair, damaged pack/index handling, and orphaned pack-related file detection.

Important control flow: saves sample data, runs normal and quick fsck, tests par2 availability, damages idx and pack files with `bup damage`, checks repair return codes with and without par2, rejects empty par2 index/volume files, over-damages packs, and finally verifies fsck reports lingering files without corresponding `.pack`.

State and dependencies: mutates pack, idx, par2, and arbitrary pack-directory files. Depends on `bup fsck`, `damage`, `gc`, `rm --unsafe`, optional par2, and Git pack layout.

Risks covered: repair code must distinguish index-only damage from pack damage, avoid accepting empty par2 artifacts, and report orphaned sidecar files after GC.
