## sources/sync-backup/bup/test/ext/test-index

Purpose: broad functional test for `bup index` and save interactions with index state.

Important control flow: checks exclude-file failure, empty index status, missing path behavior, indexing directories/files, status output for added/modified/fake-valid/fake-invalid paths, relative path output, save requirements, fifo handling, removal after reindex, tree regeneration when no files changed, and remote save argument validation.

State and dependencies: manipulates `$BUP_DIR/bupindex`, filesystem content, symlinks, fifos, and temp repo refs. Depends on `bup index`, `bup save`, `bup random`, and remote `-:repo`.

Risks covered: index correctness across file types, stale index entries, status formatting, and save/index consistency.
