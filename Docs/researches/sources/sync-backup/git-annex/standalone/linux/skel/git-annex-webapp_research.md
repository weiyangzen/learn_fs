<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-webapp -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-annex-webapp

Purpose: Linux standalone launcher for `git-annex webapp`.

Control flow: same base resolution as other Linux skeleton wrappers, then `exec "$base/runshell" git-annex webapp "$@"`.

State and integration: delegates environment setup and any app-base behavior to `runshell`. Runtime persistence belongs to git-annex webapp, not the wrapper.

Risks: unlike the macOS wrapper, this one runs in the foreground via `exec`. A missing `runshell` or wrong bundle layout prevents launch.

Test signals: invoke webapp with help/version-style arguments where possible, verify foreground behavior, and confirm bundled environment variables are set.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-webapp -->
