## sources/sync-backup/bup/test/ext/test-import-rdiff-backup

Purpose: integration test for `bup import-rdiff-backup`.

Important control flow: skips if `rdiff-backup` is unavailable, creates an rdiff-backup archive from `lib/cmd`, ticks, updates it from `Documentation`, runs the import command into a branch, then checks save count and latest listing against `Documentation`.

State and dependencies: depends on rdiff-backup command availability, Bup init/import, and filesystem listings.

Risks covered: import script argument handling, increment listing/restoration, timestamped saves, and latest content correctness.
