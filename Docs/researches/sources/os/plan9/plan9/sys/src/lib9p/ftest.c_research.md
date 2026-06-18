# File Research: sources/os/plan9/plan9/sys/src/lib9p/ftest.c

This is a small test program for the in-memory lib9p file tree.

Key behavior:
- Creates a tree with `mktree`.
- Creates two root directories, `hello` and `goodbye`.
- Creates `world` files under both directories.
- Dumps the tree with `fdump`.
- Removes one `world` file and dumps the tree again.

Role:
- Exercises basic create, nested create, remove, and tree dump behavior.
- Depends on test/helper APIs visible through `9p.h`, including `mktree`, `fcreate`, `fremove`, and `fdump`.
