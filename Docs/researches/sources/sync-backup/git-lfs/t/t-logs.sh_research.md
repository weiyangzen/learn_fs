# sources/sync-backup/git-lfs/t/t-logs.sh

## Purpose

Tests `git lfs logs` output after an invalid log lookup has produced a Git LFS log file. It verifies the failure exit code, the stored command text in the log, and `git lfs logs last` replaying the newest log exactly.

## Important APIs, control flow, and dependencies

The test initializes a repo, runs `git lfs logs boomtown` with `set +e`, expects exit code `2`, finds the generated filename under `.git/lfs/logs`, greps the log for `$ git-lfs logs boomtown`, and compares the log file content to `git lfs logs last`.

## State, dependencies, integration points, risks, and test signals

State is the LFS logs directory and command failure metadata. Integration points are log file creation on command errors, `last` alias resolution, and log display. Risks include not writing logs on failure, using the wrong latest log, omitting the command line from the log, or returning the wrong error status. Signals are exit code `2`, the `.git/lfs/logs` file, the command-line grep, and exact equality with `git lfs logs last`.
