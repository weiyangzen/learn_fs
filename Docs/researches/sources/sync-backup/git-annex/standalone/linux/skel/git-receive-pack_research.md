<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-receive-pack -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-receive-pack

Purpose: Linux standalone launcher for bundled `git-receive-pack`, allowing Git smart protocol operations to use bundled Git.

Control flow: resolves and canonicalizes the skeleton base, validates `runshell`, then `exec "$base/runshell" git-receive-pack "$@"`.

State and integration: stateless wrapper used by remote Git transports and SSH commands. Environment setup is centralized in `runshell`.

Risks: remote protocol correctness depends on stdout/stderr behavior of the underlying command; wrapper diagnostics only happen before exec. Path resolution is the main failure surface.

Test signals: run `git receive-pack` protocol smoke tests through the wrapper against a temporary repository.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-receive-pack -->
