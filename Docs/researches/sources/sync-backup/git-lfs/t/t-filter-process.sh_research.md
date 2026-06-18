# sources/sync-backup/git-lfs/t/t-filter-process.sh

## Purpose

Validates Git's long-running `filter.lfs.process` integration. It covers clone/checkout smudge behavior, include/exclude filtering, clean behavior during add/hash-object, pointer extensions, skip-smudge checkout-index behavior, and avoiding SSH network use during `git archive`.

## Important APIs, control flow, and dependencies

The file requires Git 2.11+, configures `filter.lfs.process=git-lfs filter-process` while disabling clean/smudge fallbacks, and uses `GIT_TRACE_PACKET`. Tests create remotes, track `*.dat`, push branches, clone, checkout branches, configure global `lfs.fetchinclude`/`fetchexclude`, use `setup_case_inverter_extension`, inspect staged blobs with `git cat-file -p :path`, run `git hash-object --stdin --path`, `git checkout-index -af`, `git lfs pointer --check`, `git archive`, and pure SSH setup.

## State, dependencies, integration points, risks, and test signals

State includes the filter-process packet session, working tree files, index pointer blobs, local LFS objects, extension-transformed objects, global path-filter config, and SSH URL config. Integration points are Git filter protocol, clean/smudge ordering, pointer extension clean/smudge hooks, path filter matching, hash-object streaming, checkout-index, and archive export. Risks include filter-process hangs, choosing clean/smudge over process, wrong include/exclude smudge decisions, extension OID mismatch, 1024-byte boundary regressions, or unwanted SSH calls from archive. Signals are worktree content equality, pointer assertions, extension log greps, hash equality, pointer-check success, and absence of pure SSH trace in archive logs.
