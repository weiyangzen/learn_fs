# sources/sync-backup/bup/lib/bup/cmd/tag.py

## Purpose
`tag.py` lists, creates, overwrites, or deletes lightweight bup/git tags under `refs/tags`.

## APIs and Control Flow
`main(argv)` checks the repo and flattens `git.tags()` values. With `--delete` it verifies existence unless `--force`, then calls `git.delete_ref`. With no args it prints all tags. With two args it validates non-empty/non-dot tag name, resolves the commit via `git.rev_parse`, confirms the object exists in `PackIdxList`, and updates `refs/tags/<tag>` with force semantics.

## State, Dependencies, Integration, Risks, Tests
Persistent state is tag refs. Dependencies include `git.tags`, `rev_parse`, `PackIdxList`, `update_ref`, and `delete_ref`. Risks include comment-marked need to review safe writes, force overwrite behavior, tag listing order from git tag map, and creation of tags pointing to existing objects that may not be commits despite variable naming. Test signals include listing, missing delete with/without force, dot-prefix rejection, duplicate tag rejection, nonexistent commit handling, object existence checks, and force update.
