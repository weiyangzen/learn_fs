<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-file-with-branch-name.sh -->
# sources/sync-backup/git-lfs/t/t-push-file-with-branch-name.sh

Purpose: regression test that pushing a file whose path matches a branch name still uploads the correct LFS object and does not confuse file-path and ref-name parsing.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, regular Git commit/push, and `assert_server_object`.

Control flow: creates a file named `branch`, commits it on an LFS-tracked path, pushes `main`, and verifies the resulting object by SHA-256 on the server.

State and persistence: persists a single pointer in Git history and the matching media object in the test server's LFS object store.

Dependencies and integration points: exercises pointer generation, pre-push object enumeration, and ref/path disambiguation in Git LFS push code.

Risks: ambiguous names can cause missing uploads if revision arguments are resolved before paths or if scanner output is interpreted as refs.

Test signals: one focused integration test with explicit server-object assertion.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-file-with-branch-name.sh -->
