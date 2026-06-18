# sources/sync-backup/git-lfs/t/t-migrate-fixup.sh

## Purpose

Tests `git lfs migrate import --fixup`, which infers files to migrate from existing `.gitattributes` instead of explicit include/exclude filters. It covers simple, special-attribute, nested negation, incompatible options, remote tags, `.gitattributes` symlinks, macros, LFS macros, and no-op cases.

## Important APIs, control flow, and dependencies

The script sources `fixtures/migrate.sh`, uses setup helpers such as `setup_single_local_branch_tracked_corrupt`, computes OIDs from current Git blobs, runs `git lfs migrate import --everything --fixup --yes`, and validates pointers and local objects. It also tests failures for `--include`, `--exclude`, `--no-rewrite`, symlinked `.gitattributes`, and checks no-op behavior by comparing original and migrated HEADs.

## State, dependencies, integration points, risks, and test signals

State includes corrupted/non-pointer tracked files, `.gitattributes` content including macros and negations, remote tags, rewritten refs, and local LFS object cache. Integration points are attribute parser fixup discovery, history rewrite, pointer insertion, macro expansion, symlink protection, option validation, and no-op detection. Risks include migrating files excluded by nested attributes, allowing incompatible flags, rewriting when no files qualify, or following `.gitattributes` symlinks. Signals are pointer/object assertions, grep diagnostics, `.gitattributes` content greps, tree-mode diffs, and ref-unmoved checks.
