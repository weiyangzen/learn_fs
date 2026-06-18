# sources/sync-backup/bup/lib/bup/cmd/save.py

## Purpose
`save.py` creates bup tree and commit objects from the filesystem index, preserving metadata and hardlink relationships, and optionally updating a named backup branch.

## APIs and Control Flow
`opts_from_cmdline` validates output mode, sources, date, size/bandwidth limits, strip/strip-path/graft behavior, save name, and destination repo. `save_tree` is the core: it reads index entries, optionally precomputes progress totals, maps filesystem paths to archive paths, uses `Stack` to build nested git trees, writes `.bupm` metadata entries, reuses valid indexed object IDs, hashes changed regular files with `split_to_blob_or_tree`, writes symlinks or empty blobs for special files, validates/repackages index entries, and handles root metadata collisions. `commit_tree` writes a commit with bup trailers. `main` opens destination repo, index/metastore/hlink DB, calls `save_tree`, prints requested tree/commit IDs, and updates the named branch.

## State, Dependencies, Integration, Risks, Tests
Persistent effects include new blobs/trees/commits, optional branch update, and updated index entries. Dependencies are `hashsplit`, `index`, `metadata`, `hlinkdb`, `tree.Stack`, `repo_for_location`, `open_noatime`, and commit-message helpers. Risks include filesystem races between index and save, mode changes after indexing, root/strip/graft collisions, incorrect metadata sort-key assumptions documented in comments, sparse/hardlink metadata consistency, and remote bandwidth/client failures. Test signals include mode validation, strip/graft conflicts, index-missing error, metadata `.bupm` ordering, changed-file hashing, skipped large files, branch parent update, and progress math.
