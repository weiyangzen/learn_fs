# sources/test-tools/unionmount-testsuite/tests/hard-link-dir.py

Purpose: verifies that hard-link operations involving directories fail correctly and leave directory state intact.

Important APIs/types/functions: eight `subtest_*` functions using `ctx.link`, `ctx.open_dir`, `ctx.open_file`, `ctx.rmdir`, `ctx.mkdir`, and `ctx.rename`.

Control flow: tests hard-linking a directory to a missing name (`EPERM`), linking files over dirs and dirs over files/dirs (`EEXIST`), linking a dir over itself or parent, linking removed directories (`ENOENT`), and linking renamed directories. Follow-up opens confirm original and target names.

State and persistence: some subtests create, rename, or remove directories before failed link attempts; expected state is maintained in the context tree.

Dependencies and integration: depends on `context.link` hardlink metadata checks and setup lower directories.

Risks: terminal slashes can change errors; overlayfs redirect_dir/xdev behavior can affect prior rename setup.

Test signals: validates directory hardlink prohibition and no accidental copy-up/name creation.
