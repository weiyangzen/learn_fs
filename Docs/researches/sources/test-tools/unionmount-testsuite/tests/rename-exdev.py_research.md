# sources/test-tools/unionmount-testsuite/tests/rename-exdev.py

Purpose: alternate directory rename tests for overlayfs configurations where `redirect_dir` is disabled and directory renames should fail with `EXDEV`.

Important APIs/types/functions: four `subtest_*` functions using `ctx.rename`, `ctx.open_dir`, and `ctx.open_file`.

Control flow: attempts to rename empty and populated directories within the same parent and into another parent. Each expects `EXDEV`, then verifies the destination remains absent and the original source and contents remain readable.

State and persistence: no successful rename should occur; source dentries remain in place.

Dependencies and integration: selected by `run` when overlayfs redirect_dir is off or `--xdev` is used.

Risks: if kernel auto-enables redirect_dir unexpectedly, these tests fail because rename succeeds instead of `EXDEV`.

Test signals: validates backward-compatible overlayfs behavior without directory redirects.
