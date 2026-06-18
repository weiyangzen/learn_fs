<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-upload-redirect.sh -->
# sources/sync-backup/git-lfs/t/t-upload-redirect.sh

Purpose: verifies that LFS uploads follow server-provided redirects correctly.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, content that triggers redirect behavior, `git push`, and `assert_server_object`.

Control flow: creates and commits an LFS file whose upload action redirects, pushes it, and confirms the object is stored.

State and persistence: persists one LFS object in remote storage after redirect handling.

Dependencies and integration points: integrates with batch API action parsing, HTTP redirect handling, authentication, and upload transfer code.

Risks: redirect handling can lose headers, credentials, or request body, causing failed uploads or security-sensitive cross-host behavior.

Test signals: one redirect upload case.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-upload-redirect.sh -->
