# sources/sync-backup/git-lfs/t/cmd/lfstest-testutils.go

Purpose: command-line bridge exposing Go test utility repo helpers to shell tests.

Important APIs/types/functions: `TestUtilRepoCallback`, `main`, and `AddCommits`.

Control flow: dispatches subcommands, currently `addcommits`. It verifies the current directory contains `.git`, wraps it as a util `Repo`, reads JSON `[]*CommitInput` from stdin, calls `repo.AddCommits`, and writes JSON `[]*CommitOutput` to stdout.

State/persistence behavior: mutates the current Git repository by adding commits/files/tags/branches according to JSON input. Does not call `Cleanup` because shell tests own the repo.

Dependencies/integration: imports `t/cmd/util` to share Go repo-construction logic with shell tests.

Risks: refuses to run outside repo root, but still modifies the current repo directly. JSON errors or Git failures exit with nonzero codes.

Test signals: stdout commit metadata and repository history changes.
