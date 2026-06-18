<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-p2p-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-p2p-annex

Purpose: macOS app-bundle launcher for the P2P annex remote helper.

Control flow: shared macOS launcher pattern ending with `exec "$base/runshell" git-remote-p2p-annex "$@"`.

State and integration: no persistent wrapper state; P2P configuration and sockets belong to the invoked helper and git-annex.

Risks: app-bundle path resolution and helper discoverability are the main wrapper concerns.

Test signals: Git remote-helper invocation for a P2P annex remote through the macOS bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-p2p-annex -->
