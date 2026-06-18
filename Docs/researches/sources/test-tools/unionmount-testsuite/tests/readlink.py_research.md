# sources/test-tools/unionmount-testsuite/tests/readlink.py

Purpose: validates `readlink` on files, directories, direct/indirect symlinks, dangling symlinks, and absent paths.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.readlink`.

Control flow: regular files and directories expect `EINVAL`; direct and indirect symlinks to files or dirs return their stored symlink contents; absent files expect `ENOENT`; dangling symlinks return their link text rather than following to the missing target.

State and persistence: read-only; no filesystem mutation is intended.

Dependencies and integration: depends on setup symlink values and context `readlink` no-follow behavior.

Risks: terminal slash on symlinks can convert expected results to slash traversal errors through context override logic.

Test signals: covers symlink metadata preservation and no-follow lookup across overlay layers.
