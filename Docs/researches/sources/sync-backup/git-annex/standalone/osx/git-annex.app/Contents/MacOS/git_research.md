<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git

Purpose: macOS app-bundle launcher for bundled `git`.

Control flow: resolves a simple symlink with `readlink "$0"`, derives and validates `base` and `base/runshell`, canonicalizes base, exports `GIT_ANNEX_APP_BASE` when the standalone app marker `base/git-annex` exists, then executes `"$base/runshell" git "$@"`.

State and dependencies: stateless wrapper; depends on `/bin/sh`, `readlink`, and the macOS app's `runshell`.

Integration points and risks: links app-bundle command stubs to the shared macOS runtime setup. Unlike Linux wrappers, it does not use `readlink -f`, matching macOS tool availability. Test with app translocation/symlink layouts is important.

Test signals: invoke through the app bundle and through symlinks, verify app base export and argument forwarding.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git -->
