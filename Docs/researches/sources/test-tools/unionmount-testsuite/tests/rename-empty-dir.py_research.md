# sources/test-tools/unionmount-testsuite/tests/rename-empty-dir.py

Purpose: broad coverage of empty directory rename, removal, overwrite, self-rename, and wrong-type targets.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.rename`, `ctx.rmdir`, `ctx.unlink`, `ctx.open_dir`, and `ctx.open_file`.

Control flow: renames empty dirs away and back, removes/unlinks old names, removes then tries rename, renames twice, rejects rename over populated dir with `ENOTEMPTY`, allows self-rename, rejects rename over files with `ENOTDIR`, and rejects over the parent test directory with `ENOTEMPTY`.

State and persistence: successful renames update directory dentries and may rotate upper layers in recycle mode; removals create whiteouts/negative dentries.

Dependencies and integration: context rename/rmdir/unlink state machine and overlayfs directory rename support.

Risks: errno behavior for empty dir over non-empty dir can be `ENOTEMPTY` or `EEXIST`; context tolerates some variants.

Test signals: dense coverage for directory whiteout/redirect/copy-up state.
