# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.c

Local canonical path resolver.

`myrealpath()` resolves relative paths using `getcwd()`, normalizes `.`, `..`, and repeated slashes, resolves symlinks with `readlink()`, and limits symlink traversal with `MAX_READLINKS`. It writes into a caller-provided buffer and returns `NULL` with `errno` on path length or symlink-loop errors.

This is bundled because the comment says the libc version had security flaws in the environment this code originated from.
