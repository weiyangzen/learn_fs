# sources/sync-backup/git-lfs/t/t-migrate-export.sh

## Purpose

Broad integration coverage for `git lfs migrate export`, which rewrites history from LFS pointers back to normal Git blobs. It covers local and remote refs, bare repositories, include/exclude filters, given branches, required filters, excluding remote refs, `--skip-fetch`, include/exclude ref selection, invalid refs/remotes, `.gitattributes` mode/symlink handling, object maps, verbose output, remote override, and invalid pointer robustness.

## Important APIs, control flow, and dependencies

The file sources `fixtures/migrate.sh`, uses setup helpers for tracked local/remote branch topologies, calculates OIDs from worktree content, calls `git lfs migrate export` with `--include`, `--exclude`, `--everything`, `--skip-fetch`, `--include-ref`, `--exclude-ref`, `--object-map`, `--verbose`, and `--remote`, and validates rewritten refs with `assert_pointer`/`refute_pointer`, local object pruning helpers, `.gitattributes` content checks, tree mode diffs, and commit-map diffs.

## State, dependencies, integration points, risks, and test signals

State includes rewritten Git refs, remote-tracking refs, tags, LFS object cache, `.gitattributes` blobs and modes, object map files, and downloaded/missing media. Integration points are history rewrite planning, pointer smudging into blobs, remote fetch/prune decisions, ref include/exclude filters, attribute mutation to `!text !filter !merge !diff`, object pruning, bare repo support, and object-map generation. Risks include rewriting unintended remote refs, pruning still-referenced objects, losing executable/symlink semantics, failing when objects must be downloaded, or producing incomplete object maps. Signals are pointer/refutation assertions, local object presence matrices, grep checks in `.gitattributes`, invalid-input diagnostics, tree diffs, verbose commit output, and sorted object-map diffs.
