<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-webapp -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-webapp

Purpose: macOS app-bundle launcher for `git-annex webapp`.

Control flow: performs normal macOS base resolution and `GIT_ANNEX_APP_BASE` export, then starts `"$base/runshell" git-annex webapp "$@"` in the background. The backgrounding is explicit because macOS app launch behavior expects the wrapper to return.

State and integration: wrapper has no durable state; the webapp and runshell handle runtime state, environment, and self-install hooks.

Risks: backgrounding means caller exit status does not reflect long-term webapp startup success. Diagnostics after backgrounding may be detached from the launcher context.

Test signals: app launch starts the webapp without blocking, arguments are forwarded, and failure modes are observable in app logs or stderr.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-webapp -->
