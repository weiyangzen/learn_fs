# sources/sync-backup/git-lfs/t/cmd/lfstest-badpathcheck.go

Purpose: deliberately suspicious test command for path/execution safety tests.

Important API: `main`.

Control flow: prints `exploit` to stdout and stderr, then attempts to create a file named `exploit`.

State/persistence behavior: may create `./exploit` in the current directory.

Dependencies/integration: used to verify Git LFS does not execute untrusted path components or bad hooks/tools unexpectedly.

Risks: intentionally has side effects; should only be run in isolated test directories.

Test signals: presence or absence of output/file indicates whether a path execution vulnerability was triggered.
