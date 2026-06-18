## sources/sync-backup/bup/test/ext/test-index-clear

Purpose: verifies `bup index --clear` removes stale index entries.

Important control flow: indexes a directory with two files, checks path output, deletes one file, clears the index, reindexes, and verifies only the remaining file, directory, and root entries are listed.

State and dependencies: temp repo index file and filesystem tree. Depends on `bup index -p/-u/--clear`.

Risks covered: stale deleted paths must not survive after an explicit clear/reindex cycle.
