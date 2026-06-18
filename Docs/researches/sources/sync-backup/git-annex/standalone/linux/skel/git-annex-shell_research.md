<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-shell -->
# sources/sync-backup/git-annex/standalone/linux/skel/git-annex-shell

Purpose: Linux standalone launcher for `git-annex-shell`, used by SSH and remote repository access.

Control flow: resolves the wrapper base, validates `runshell`, canonicalizes the directory, and executes `"$base/runshell" git-annex-shell "$@"`.

State and integration: stateless itself, but it relies on `runshell` to install SSH helper shims and set bundled paths/libraries. It is a security-sensitive entry point because it may process SSH-original commands.

Risks: wrapper correctness depends on preserving all arguments exactly; this script quotes `"$@"`. Missing or tampered `runshell` prevents operation.

Test signals: call directly and through an SSH forced-command shim, verify command argument forwarding, and check failure diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git-annex-shell -->
