<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-annex

Purpose: Linux standalone launcher for the bundled `git-annex` command.

Control flow and APIs: identical base resolution and validation pattern to the other Linux skeleton launchers, ending with `exec "$base/runshell" git-annex "$@"`.

State and dependencies: no durable state in the wrapper; all environment setup is delegated to `runshell`.

Integration points and risks: primary user entry point for the standalone bundle. If path canonicalization fails or `runshell` is missing, it exits before invoking git-annex. Behavior with unusual symlink chains depends on `readlink -f`.

Test signals: execute `git-annex version` through the wrapper, test symlinked installation paths, and verify arguments are preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex -->
