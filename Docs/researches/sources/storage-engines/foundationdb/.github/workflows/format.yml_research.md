# sources/storage-engines/foundationdb/.github/workflows/format.yml

## Purpose
This GitHub Actions workflow enforces C/C++ formatting on pull requests to `main` and `release-7.4`.

## Important APIs, Types, And Functions
The `clang-format` job runs on `ubuntu-24.04`, checks out the pull request head SHA, installs `clang-format-19`, formats all `.c`, `.cpp`, `.h`, and `.hpp` files while pruning `contrib`, then runs `git diff --exit-code`.

## Control Flow
On PR events, the job modifies files in place and fails if formatting produced any diff. It uses read-only content permissions.

## State And Persistence Behavior
The workflow mutates only the ephemeral Actions checkout. No repository state is committed by the job.

## Dependencies And Integration Points
It depends on `actions/checkout` pinned by SHA, Ubuntu apt, clang-format 19, and GitHub branch filters.

## Risks And Edge Cases
The `find` expression excludes all `contrib` paths and may miss generated or differently suffixed C++ files. Installing from apt makes the exact package availability tied to Ubuntu 24.04 repositories.

## Test Signals
Any formatting drift appears as a non-empty git diff and failed CI job.
