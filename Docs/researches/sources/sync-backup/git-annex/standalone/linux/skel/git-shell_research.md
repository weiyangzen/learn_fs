<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-shell -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-shell

Purpose: Linux standalone launcher for bundled `git-shell`.

Control flow: resolves base via `readlink`, checks `runshell`, canonicalizes base, and executes `"$base/runshell" git-shell "$@"`.

State and integration: stateless wrapper for SSH-restricted Git access using the bundle's Git implementation.

Risks: because `git-shell` can be exposed over SSH, preserving arguments and using the correct bundled binary matters. The wrapper itself has simple path-layout failure modes.

Test signals: execute allowed and disallowed git-shell commands through the wrapper in a temporary environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-shell -->
