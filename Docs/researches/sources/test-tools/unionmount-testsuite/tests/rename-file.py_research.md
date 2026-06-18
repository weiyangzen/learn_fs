# sources/test-tools/unionmount-testsuite/tests/rename-file.py

Purpose: tests regular file rename behavior across missing names, removals, wrong-type targets, replacement, and self-rename.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.rename`, `ctx.unlink`, `ctx.rmdir`, `ctx.open_file`, and `ctx.open_dir`.

Control flow: renames a file away and back, unlinks/rmdirs old names, rejects operations after source removal, renames twice, replaces another file, self-renames, rejects rename over directories with `EISDIR`, and rejects rename over the parent directory with `ENOTEMPTY`. Readbacks verify content and missing names.

State and persistence: successful renames copy up file metadata/data as needed, replace dentries, and create negative old names. Replacement over a file changes the destination content.

Dependencies and integration: context rename model, lower regular files, whiteout behavior, and content validation.

Risks: directory target errno can vary; each subtest depends on fresh fixture numbering.

Test signals: key regular-file rename and replacement coverage.
