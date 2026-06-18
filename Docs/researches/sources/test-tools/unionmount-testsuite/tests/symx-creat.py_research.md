# sources/test-tools/unionmount-testsuite/tests/symx-creat.py

Purpose: tests `O_CREAT` through a dangling symlink without truncation. It should create the missing target and allow normal reads/writes through the link.

Important APIs and functions: five subtests use `ctx.pointless()`, `ctx.no_file()`, and `ctx.open_file()` with create and access mode flags.

Control flow: read-only create checks an empty created file. Write and read/write cases create then write `q`; append cases also create and append `q`, resulting in the same one-byte content for a new file.

State and persistence: the target file is newly created in the upper layer while the symlink object remains intact.

Dependencies and integration: depends on the context's broken symlink target matching `ctx.no_file()`.

Risks: if trailing slash mode is active, a dangling symlink path may produce directory-related errors in some operations; the test expects harness-normalized Linux behavior.

Test signals: target file becomes readable with empty or `q` content after open through the dangling symlink.
