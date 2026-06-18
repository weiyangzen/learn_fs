## sources/sync-backup/bup/test/ext/test-comparative-split-join

Purpose: compares current Bup split/join behavior and repository artifacts against another Bup executable specified by `BUP_TEST_OTHER_BUP`.

Important control flow: skips without the other executable, classifies versions by pack-name algorithm, then for size 0 and five random sizes creates parallel repos, writes random data, compares split tree ids, compares joined data, optionally compares pack/index files, normalizes HEAD/repo-id differences, and compares repository trees.

State and dependencies: uses random seeds, temp repos, `bup random`, `split -t`, `join`, Git config, and `dev/compare-trees`.

Risks covered: split determinism, join compatibility, pack format changes across versions, default branch name changes, and repo-id/umask differences.
