<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git -->
# sources/sync-backup/git-annex/standalone/linux/skel/git

Purpose: Linux standalone launcher for bundled `git`.

Control flow: resolves the launcher path with `readlink -f "$0"` falling back to `readlink "$0"`, derives `base`, verifies `base` and `base/runshell`, canonicalizes `base` through `cd`/`pwd`, then `exec`s `"$base/runshell" git "$@"`.

State and dependencies: no persistent state; depends on POSIX shell, `readlink`, `dirname`, and the co-located `runshell`.

Integration points and risks: this wrapper ensures git runs inside the standalone environment established by `runshell`. It fails fast with diagnostic messages when moved away from its skeleton. Symlink and path behavior depends on platform `readlink` semantics.

Test signals: invoke through real path and symlink, move/copy without `runshell` to check failure, and verify bundled git is first in the environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/git -->
