# sources/user-network-fs/sshfs/test/pytest.ini

Purpose: pytest defaults for the sshfs test suite.

Important APIs/types/functions: `addopts` enables verbose output, assertion rewrite, native tracebacks, stop after first failure, and summary reporting; marker `uses_fuse` identifies tests requiring FUSE.

Control flow: pytest applies these defaults when run in the test directory or with this config discovered.

State and persistence behavior: no state; test runner configuration only.

Dependencies and integration points: used by CI pytest commands.

Risks: `-x` stops on first failure, which can reduce full failure visibility in local runs despite CI using `--maxfail=99` overrides in some workflows.

Test signals: pytest collection recognizes the `uses_fuse` marker without warnings.
