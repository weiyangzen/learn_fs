<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/git_clone_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/git_clone_test.go

## Purpose

This file tests whether common Git workflows can run on a gcsfuse mount under the interrupt test configuration, including `--ignore-interrupts` variants and streaming write settings chosen by package setup. The scenarios cover clone, checkout, empty commit, and committing a newly created 1 MiB file.

## Important APIs, Types, and Functions

`ignoreInterruptsTest` is a Testify suite with `SetupTest` creating `testDirPath` through `setup.SetupTestDirectory`. `cloneRepository` executes `git clone` via `operations.ExecuteToolCommandfInDirectory` with retry handling for transient GitHub/network errors. Helpers `checkoutBranch`, `emptyCommit`, `gitAdd`, `nonEmptyCommit`, and `setGithubUserConfig` run Git subcommands inside the cloned repository.

## Control Flow

Each test starts from a fresh mount test directory. Clone retries up to five times, sleeping a randomized 1 to 2000 ms on DNS, remote-read, or GitHub connection errors. Checkout clones first and switches to `test-branch`. Empty commit clones, configures local author identity, and runs `commit --allow-empty`. Commit-with-changes clones, configures identity, creates a 1 MiB file with `operations.CreateFileOfSize`, runs `git add`, then commits.

## State and Persistence Behavior

The main state is the cloned Git repository tree under the mounted test directory, including `.git`, working tree files, index updates, and commit objects written through gcsfuse. `testDirPath` is package global and reset per test. No explicit teardown removes the repository in this file; the broader package setup handles mount/test directory cleanup.

## Dependencies and Integration Points

The test depends on network access to `https://github.com/gcsfuse-github-machine-user-bot/test-repository.git`, the host `git` binary, shared operations/setup utilities, and `internal/cache/util.MiB`. It is driven by `interrupt_test.go`, which mounts with ignore-interrupt and streaming-write flag combinations.

## Risks and Test Signals

Network flakiness is partially mitigated but GitHub availability, credentials policy, and repository contents remain external dependencies. Git output is surfaced in failures. Strong signals are successful clone, branch checkout, and repository mutations without interrupted syscalls or write-path corruption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/git_clone_test.go -->
