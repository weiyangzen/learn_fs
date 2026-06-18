<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-upload-pack -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-upload-pack

Purpose: Linux standalone launcher for bundled `git-upload-pack`, used by fetch/clone smart protocol operations.

Control flow: shared skeleton base validation and canonicalization, then `exec "$base/runshell" git-upload-pack "$@"`.

State and integration: stateless wrapper used by Git transports, with environment setup delegated to `runshell`.

Risks: any pre-exec diagnostics could interfere with Git protocol if emitted after protocol negotiation, but this script only emits before exec on fatal layout errors. Path resolution remains the main wrapper risk.

Test signals: clone/fetch from a repository using this wrapper as the upload-pack command and verify protocol success.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-upload-pack -->
