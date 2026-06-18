<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push.sh -->
# sources/sync-backup/git-lfs/t/t-push.sh

Purpose: broad integration suite for `git lfs push`, covering refs, `--all`, `--object-id`, stdin input, remote selection, retries, raw URLs, invalid metadata, href rewriting, server-already-has-object optimization, tags, and custom refs.

Important APIs/functions: defines `push_repo_setup` and `push_all_setup`; uses `setup_remote_repo`, `clone_repo`, `setup_alternate_remote`, `lfstest-testutils addcommits`, `git lfs push`, `git push`, `assert_server_object`, `refute_server_object`, `delete_local_object`, `calc_oid`, and `get_date`.

Control flow: early tests validate ref requirements and remote precedence. The main push case checks dry-run output, stdin refs, remote ref simulation, and actual upload counts. `push_all_setup` builds multi-commit branch/tag histories, then `--all` tests ensure correct object sets for no refs, one ref, multiple refs, and deleted files. Later tests validate object-ID-only upload, stdin object IDs, modified-file histories, invalid remotes, ambiguous branch/tag names, expired action retry, raw remote URLs, invalid object sizes, deprecated `_links`, invalid `pushInsteadOf` href rewrite, skipping objects the server already has, multi-ref tag behavior, custom namespaces, and invalid OID diagnostics.

State and persistence: repeatedly creates bare remotes, clones, branch/tag histories, `.git/refs/remotes/origin/HEAD` simulations, local object deletions, config keys such as locks verification and href rewriting, and remote LFS object storage.

Dependencies and integration points: spans the pre-push hook, command-line push path, object scanner, rev-list traversal, batch API, transfer queue, remote URL resolution, Git config remote precedence, retry logic, and test server status/content triggers.

Risks: this is high-blast-radius behavior. Regressions could miss historical objects, upload deleted/unwanted objects, fail multi-ref pushes, re-upload known objects, honor the wrong remote, mis-handle raw URLs, or panic on malformed server metadata.

Test signals: over twenty integration blocks cover valid and invalid refs, `--all`, `--object-id`, stdin warnings, retries, raw URL push, invalid sizes, href rewrite failure, server object de-duplication, multi-ref/tag pushes, custom references, and invalid object-ID errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push.sh -->
