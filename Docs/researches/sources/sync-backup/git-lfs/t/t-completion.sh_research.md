# sources/sync-backup/git-lfs/t/t-completion.sh

## Purpose
Tests the `git lfs completion` command for supported shells and argument validation. It ties generated completion output to checked-in fixtures.

## Important APIs, Functions, and Control Flow
The script runs `git lfs completion bash`, `fish`, and `zsh`, comparing stdout byte-for-byte against fixtures in `$COMPLETIONSDIR`. It also runs the command with no shell argument and with invalid shell `ksh`, then greps for validation errors.

## State, Persistence, and Dependencies
The tests only create temporary logs and rely on `$COMPLETIONSDIR`. Dependencies are fixture files, `cmp`, and Cobra argument validation messages.

## Integration Points, Risks, and Test Signals
Integration is with CLI completion generation. Signals are exact fixture comparisons plus `accepts 1 arg` and `invalid argument` text. Risks are high fixture churn whenever generated completion templates change.
