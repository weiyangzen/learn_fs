# sources/test-tools/unionmount-testsuite/tests/hard-link-sym.py

Purpose: tests hard-link behavior for symlinks, dangling symlinks, and symlinks after unlink/rename.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.link`, `ctx.open_file`, `ctx.unlink`, and `ctx.rename`.

Control flow: creates hard links to direct and dangling symlinks, verifies both names resolve the same way, rejects links over existing files/new files/symlinks with `EEXIST`, rejects missing sources with `ENOENT`, and validates unlinked/renamed symlink source behavior.

State and persistence: successful links add additional directory entries sharing the symlink inode metadata; later opens validate target content or dangling errors.

Dependencies and integration: depends on `context.link` no-follow/follow behavior, setup symlinks, and errno expectations.

Risks: POSIX hardlink symlink-following behavior differs by flags and platform; context defaults are Linux-oriented.

Test signals: validates overlayfs handling of symlink hardlinks and whiteout/copy-up state after rename/unlink.
