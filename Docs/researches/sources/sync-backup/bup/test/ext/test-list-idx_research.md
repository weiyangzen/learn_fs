## sources/sync-backup/bup/test/ext/test-list-idx

Purpose: tests `bup list-idx` for listing and finding object hashes in pack indexes.

Important control flow: initializes a repo, saves random data, runs `bup list-idx` on generated `.idx` files, extracts a hash from output, then runs `list-idx --find HASH` and verifies the found hash matches and exactly one output line is produced.

State and dependencies: temp repo pack/index files created by `bup save`. Depends on `bup random`, `index`, `save`, and `list-idx`.

Risks covered: pack index parsing and exact-match lookup behavior.
