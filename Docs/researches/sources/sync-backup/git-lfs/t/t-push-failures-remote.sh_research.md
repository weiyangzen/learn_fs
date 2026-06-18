<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-remote.sh -->
# sources/sync-backup/git-lfs/t/t-push-failures-remote.sh

Purpose: verifies push error reporting when the server returns failure responses from either storage upload endpoints or the batch API.

Important APIs/functions: defines `push_fail_test`; uses `setup_remote_repo`, `clone_repo`, `repo_endpoint`, `git lfs track`, `git push`, and server-triggering content names such as `return-status-403`.

Control flow: `push_fail_test` creates a repo, writes a file whose payload causes the test server to emit a chosen status, commits it, attempts a push, and asserts the command fails with the expected status text. It parameterizes storage-layer and API-layer failures.

State and persistence: creates one disposable remote per case, commits a single LFS-tracked file, and relies on the test server's content-triggered response behavior rather than persistent error configuration.

Dependencies and integration points: integrates with the batch transfer client, HTTP status handling, LFS pre-push hook, credential helper, and lfstest server error simulation.

Risks: regressions here would hide authorization, missing object, gone, validation, and server-error messages from users, or could accidentally retry/continue after unrecoverable statuses.

Test signals: ten cases cover storage 403/404/410/500/503 and API 403/404/410/422/500 responses.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-remote.sh -->
