# sources/test-tools/unionmount-testsuite/tests/symx-creat-trunc.py

Purpose: verifies that `O_CREAT|O_TRUNC` through a dangling symlink creates the missing target file and writes or reads through it.

Important APIs and functions: five subtests use `ctx.pointless()`, `ctx.no_file()`, and `ctx.open_file()` with `crt=1, tr=1` plus access mode variants.

Control flow: read-only create/truncate yields an empty newly created target. Write and append variants create/truncate then write `q`, and read the previously absent target path to confirm contents.

State and persistence: the dangling symlink remains, while its target path becomes a new upper-layer file. The target content is empty or `q` depending on mode.

Dependencies and integration: depends on harness fixture alignment where `ctx.pointless()` resolves to `ctx.no_file()`. Exercises symlink-following creation in overlay.

Risks: `O_CREAT|O_TRUNC|O_RDONLY` through dangling symlink is subtle and Linux-specific. The local variable `f` is only used for validation, not for setup.

Test signals: successful open through the symlink and target file content visible at `ctx.no_file()`.
