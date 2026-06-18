
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/prep-auto-dir -->
# Research: sources/sync-backup/rsync/packaging/prep-auto-dir

## Purpose
`packaging/prep-auto-dir` manages rsync's branch-specific auto build directory. It moves the real `build` directory in and out of `auto-build-save/<branch>`, preserving a stable real `build` path for ccache efficiency while keeping branch-specific build artifacts separated.

## Important APIs, Types, and Functions
This POSIX shell script has no functions. Key variables are `auto_top=auto-build-save`, `desired_branch` from `git rev-parse --abbrev-ref HEAD | tr / %`, `auto_dir`, and `cur_branch` from `build/.branch`.

## Control Flow
If `auto-build-save` and `.git` both exist, the script determines the current branch, rejects detached HEAD, compares it to the branch currently represented by `build/.branch`, and if they differ moves the current `build` directory back under `auto-build-save/<old>`, creates the desired branch directory as needed, makes `.branch` and reverse symlinks, and moves the desired directory to `build`. It also ensures top-level `Makefile` is a symlink to `packaging/auto-Makefile`, then echoes the branch id.

## State and Persistence
It persistently moves directories and symlinks: `build`, `build/.branch`, `auto-build-save/<branch>`, and top-level `Makefile`. It does nothing when the expected auto-build top directory is absent, allowing normal builds.

## Dependencies and Integration Points
It depends on `git`, `readlink`, `mv`, `ln`, and shell utilities. `packaging/smart-make` calls it and switches into `build` when it prints a branch name. `pkglib.get_gen_files()` expects the same `auto-build-save/<branch>` convention.

## Risks
Directory moves are destructive if the layout is manually altered or `.branch` is stale. The script does not quote `$auto_top` in all tests, although the values are controlled. It refuses detached HEAD rather than handling it. Interrupted moves could leave `build` and `auto-build-save` inconsistent.

## Test Signals
Use temporary git repositories to exercise first setup, branch switch, existing build preservation, detached HEAD refusal, and Makefile symlink creation. Verify ccache-sensitive real `build` path stays consistent after switches.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/prep-auto-dir -->
