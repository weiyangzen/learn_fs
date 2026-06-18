# sources/test-tools/unionmount-testsuite/tests/symx-trunc.py

Purpose: verifies truncating opens through a dangling symlink without `O_CREAT` fail because the target does not exist.

Important APIs and functions: five subtests use `ctx.pointless()` and `ctx.open_file(..., tr=1)` with mode variants, expecting `ENOENT`.

Control flow: each subtest attempts `O_TRUNC` through the dangling symlink and asserts the absent-target error.

State and persistence: no target file should be created or truncated. The dangling symlink should remain.

Dependencies and integration: relies on Linux open semantics and harness mapping of `tr=1` to `O_TRUNC`.

Risks: exact behavior for `O_TRUNC|O_RDONLY` can be implementation-specific, but the intended Linux result here is `ENOENT` for the unresolved target.

Test signals: every truncating open without create returns `ENOENT`.
