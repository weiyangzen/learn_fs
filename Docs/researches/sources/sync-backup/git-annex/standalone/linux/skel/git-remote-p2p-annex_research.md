<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-p2p-annex -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-remote-p2p-annex

Purpose: Linux standalone launcher for the P2P annex Git remote helper.

Control flow and integration: shares the standard Linux skeleton wrapper logic and executes `"$base/runshell" git-remote-p2p-annex "$@"`, ensuring the helper runs with bundled binaries and libraries.

State and dependencies: stateless; depends on `runshell` and the bundled helper existing in the bundle path configured by `runshell`.

Risks: P2P remotes may be invoked by Git automatically, so missing wrapper placement in `PATH` breaks discovery. Path canonicalization and `runshell` integrity are the wrapper-level risks.

Test signals: invoke helper discovery through Git and run a minimal P2P remote operation through the standalone bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-remote-p2p-annex -->
