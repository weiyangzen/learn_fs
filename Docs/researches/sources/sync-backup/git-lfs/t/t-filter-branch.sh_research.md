# sources/sync-backup/git-lfs/t/t-filter-branch.sh

## Purpose

Regression test for running Git LFS tracking inside `git filter-branch` tree filters. It ensures repeated history rewriting with LFS clean filters produces valid pointers and local objects for every rewritten `.dat` file.

## Important APIs, control flow, and dependencies

The test creates three commits containing `a.dat`, `b.dat`, and `c.dat`, then runs `git filter-branch -f --prune-empty --tree-filter` that removes all cached files, runs `git lfs track "*.dat"`, and re-adds the tree for all refs/tags. It then calls `assert_pointer` for all files on `main`.

## State, dependencies, integration points, risks, and test signals

State includes rewritten Git history, `.gitattributes`, pointer blobs, and local LFS object cache. Integration points are Git tree-filter execution, clean filter behavior, index rewriting, and pointer creation during history rewrite. Risks include filter-branch recursion, stale index state, missing LFS objects, or noncanonical pointers after rewrite. Signals are `assert_pointer` checks with calculated OIDs and sizes for all three files.
