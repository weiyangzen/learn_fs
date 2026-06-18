# sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff_test.go

## Purpose
Tests `patch-diff` behavior in a temporary git repository with a modified source file.

## Important APIs, Types, and Functions
Uses `vcs.MakeTestRepo`, `osutil.WriteFile`, `aflow.TestTool`, and regex cleanup for dynamic git index lines.

## Control Flow
The test commits a C file, changes one line, verifies expanded-context diff output, restricts to `foo.c`, checks nonexistent file empty output, and verifies outside-repo bad-call conversion.

## State and Persistence Behavior
All mutations occur in a temp git repo. No persistent state remains.

## Dependencies and Integration Points
Depends on git diff output format and aflow test harness.

## Risks and Test Signals
Good signal for command flags and path safety. It does not test timeout or very large diffs.
