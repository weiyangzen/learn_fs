# sources/sync-backup/git-lfs/t/t-migrate-import-no-rewrite.sh

## Purpose

Tests `git lfs migrate import --no-rewrite`, which imports selected current files into LFS by adding a new commit without rewriting existing history. It covers default branch, bare repo rejection/behavior, multiple branches, missing or nested `.gitattributes`, custom commit messages including empty messages, and strict path matching in complex nested directories.

## Important APIs, control flow, and dependencies

The file sources `fixtures/migrate.sh`, uses setup helpers such as `setup_local_branch_with_gitattrs`, computes OIDs from index/worktree blobs, runs `git lfs migrate import --no-rewrite --yes` with pathspecs and `-m`, checks `HEAD~1` against the previous commit to confirm history was not rewritten, and verifies new HEAD commit messages and pointers. The strict test creates nested Yarn mirror paths and explicit `.gitattributes` entries.

## State, dependencies, integration points, risks, and test signals

State includes current branch tips, prior commit IDs, new import commits, `.gitattributes` at root and nested paths, local LFS objects, and bare/non-bare repo layout. Integration points are no-rewrite import planner, pathspec matching, attribute file update, commit creation, pointer generation, and local object storage. Risks include rewriting prior commits, using a default commit message when an empty one is supplied, missing nested attributes, overmatching similar paths, or failing to add local objects. Signals are pointer/object assertions, `HEAD~1` equality with prior head, new HEAD inequality, commit-message comparisons, and strict nested path pointer checks.
