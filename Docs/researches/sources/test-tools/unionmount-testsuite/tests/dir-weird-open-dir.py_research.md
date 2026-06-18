# sources/test-tools/unionmount-testsuite/tests/dir-weird-open-dir.py

Purpose: tests existing directory opens with `O_DIRECTORY` plus create/exclusive/truncate flag combinations.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.open_dir`.

Control flow: `O_DIRECTORY|O_CREAT` combinations expect `EINVAL`; `O_DIRECTORY|O_TRUNC` without create expects `EISDIR`; `O_CREAT|O_EXCL` variants also expect `EINVAL`. Every subtest reopens the directory read-only afterward.

State and persistence: no intended mutation; failed open attempts must not alter directory layer state or contents.

Dependencies and integration: relies on `context.open_dir` translating to `open_file(dir=1)` and Linux errno semantics.

Risks: exact errno ordering can differ across kernel versions or non-overlay filesystems.

Test signals: catches regressions in `O_DIRECTORY` validation and post-error directory accessibility.
