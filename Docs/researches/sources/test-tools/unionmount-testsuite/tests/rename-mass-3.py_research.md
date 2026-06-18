# sources/test-tools/unionmount-testsuite/tests/rename-mass-3.py

Purpose: exercises repeated circular renames of existing lower regular files and later removes the resulting names. It stresses overlay/union rename bookkeeping when one name in a fixed ring is intentionally absent.

Important APIs and functions: defines `ring_size`, `iter_count`, `subtest_1(ctx)`, and `subtest_2(ctx)`. It uses `ctx.reg_file()`, `ctx.rename()`, and `ctx.unlink()` with expected `ENOENT` from `errno`.

Control flow: `subtest_1` derives a base path from a regular-file fixture prefix, then repeatedly renames `next_gap` into `gap`. `subtest_2` recomputes the final missing slot and unlinks all names, expecting `ENOENT` only for the gap.

State and persistence: persistent filesystem state is the renamed dentry sequence. No module globals mutate during execution except loop-local `gap`; correctness depends on each rename moving exactly one file.

Dependencies and integration: run by the unionmount test harness, which supplies fixture numbering and validates expected errno behavior. The test integrates with overlayfs rename/copy-up behavior through `ctx.rename`.

Risks: off-by-one ring math can mask a missing entry or unlink the wrong path. The test assumes fixture files with matching numeric suffixes exist before it runs.

Test signals: success is the absence of unexpected rename/unlink errors and exactly one `ENOENT` at cleanup.
