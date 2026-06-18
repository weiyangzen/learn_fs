# sources/sync-backup/bup/lib/bup/cmd/get.py

## Purpose
`get.py` transfers objects, commits, branches, saves, tags, or unnamed objects from a source bup/git repository to a destination repository. It supports fast-forward, append, pick, force-pick, new-tag, replace, unnamed fetch, optional rewrite/repair, and remote destination/source forms.

## APIs and Control Flow
Argument handling is custom through `argspec`, `usage`, `misuse`, `Spec`, and `parse_args`, because transfer methods carry ordered mode context. Resolvers (`resolve_src`, `resolve_ff`, `resolve_append`, `resolve_pick`, `resolve_new_tag`, `resolve_replace`, `resolve_unnamed`) validate all requested operations before writes. Handlers (`handle_ff`, `handle_append`, `handle_pick`, `handle_new_tag`, `handle_replace`, `handle_unnamed`) perform object walks with `get_random_item`, commit copying with `transfer_commit`, or save rewriting via `Rewriter`. `get_everything` compares hashsplit configs, creates a `Rewriter` when required, transfers all objects, accumulates ref updates, and updates refs only after successful writes.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are new objects and final ref updates in the destination; rewrite/repair may record repair trailers in commit messages and returns `EXIT_RECOVERED` when repairs succeed. Dependencies include `repo_for_url`, `repo_for_location`, `vfs`, `git.walk_object`, `commit_message`, `RepairInfo`, `Rewriter`, and remote client error classes. Risks include config mismatch without explicit copy/rewrite choice, `--ignore-missing` being dangerous and limited to unnamed fetches, duplicate tag targeting, remote index suggestion races handled by rechecking existence, and ref update failures after object transfer. Test signals include parser ordering, resolver misuse cases, all transfer methods, delayed ref update atomicity, repair-id validation, excludes only for rewrite/repair, and missing object handling.
