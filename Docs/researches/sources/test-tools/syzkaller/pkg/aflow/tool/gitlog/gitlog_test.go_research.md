# sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog_test.go

## Purpose
Regression tests for git-log, git-show, and git-blame aflow wrappers using synthetic repositories.

## Important APIs, Types, and Functions
Uses `vcs.MakeTestRepo`, `CommitChangeset`, `aflow.TestTool`, regex assertions, and `aflow.TestWorkdir` to point helpers at the temporary repo layout.

## Control Flow
Tests create commits, then exercise message, code, symbol, and path log modes; blame line ranges; show full commits and commit:path objects; and negative validation paths.

## State and Persistence Behavior
Creates temporary git repos under test dirs. No repository state survives tests.

## Dependencies and Integration Points
Depends on syzkaller `vcs` test helpers and aflow test harness. It validates interaction between gitlog tools and `kernel.UseLinuxRepo` workdir conventions.

## Risks and Test Signals
Strong signal for command construction and bad-call conversion. It intentionally does not cover timeouts or very large output truncation beyond core wrappers.
