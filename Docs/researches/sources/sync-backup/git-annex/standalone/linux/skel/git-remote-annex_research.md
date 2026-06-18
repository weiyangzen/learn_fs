<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-remote-annex

Purpose: Linux standalone launcher for the `git-remote-annex` transport helper.

Control flow: performs shared skeleton base lookup and validates `runshell`, then executes `"$base/runshell" git-remote-annex "$@"`.

State and integration: no wrapper state; integrates Git remote-helper discovery with the standalone environment.

Risks: if not present in `PATH`, Git will not discover the helper. The wrapper itself only checks local bundle layout.

Test signals: configure a remote using the annex helper and verify Git invokes this wrapper with arguments preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-annex -->
