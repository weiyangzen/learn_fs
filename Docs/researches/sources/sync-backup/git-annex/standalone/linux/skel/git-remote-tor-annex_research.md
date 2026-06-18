<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-tor-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-remote-tor-annex

Purpose: Linux standalone launcher for the Tor annex Git remote helper.

Control flow: standard base resolution and validation, followed by `exec "$base/runshell" git-remote-tor-annex "$@"`.

State and integration: no persistent state in the launcher; Tor/helper configuration is handled by the invoked command and the standalone environment.

Risks: remote-helper discovery depends on executable name and `PATH`. Wrapper failure modes are missing base or missing `runshell`.

Test signals: check `git-remote-tor-annex` invocation through this wrapper and a configured Tor-annex remote smoke test where available.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-tor-annex -->
