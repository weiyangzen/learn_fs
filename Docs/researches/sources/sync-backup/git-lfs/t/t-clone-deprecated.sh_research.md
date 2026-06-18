# sources/sync-backup/git-lfs/t/t-clone-deprecated.sh

## Purpose
Tests that `git lfs clone` emits a deprecation warning on sufficiently new Git versions where regular `git clone` has comparable LFS support.

## Important APIs, Functions, and Control Flow
The script gates on Git version `>= 2.15.0`, creates an empty remote, enters a directory named after the repository, runs `git lfs clone "$GITSERVER/$reponame"`, and greps the output for two warning lines.

## State, Persistence, and Dependencies
State is limited to a test remote, a local directory, and `clone.log`. Dependencies include `ensure_git_version_isnt`, `setup_remote_repo`, and the deprecation text in the `git lfs clone` command.

## Integration Points, Risks, and Test Signals
Integration is the CLI compatibility layer for the deprecated clone subcommand. Signals are exact warning text. Risks are message churn and Git version gate mismatch.
