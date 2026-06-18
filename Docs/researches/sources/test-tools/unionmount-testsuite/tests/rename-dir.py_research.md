# sources/test-tools/unionmount-testsuite/tests/rename-dir.py

Purpose: tests moving populated lower directories and populated subdirectories to sibling locations.

Important APIs/types/functions: two `subtest_*` functions using `ctx.rename`, `ctx.open_dir`, and `ctx.open_file`.

Control flow: moves a populated directory into an empty directory child path, then verifies the old name is missing, the new directory exists, and contained files are readable. A second subtest moves the `pop` subdirectory and verifies child `b`.

State and persistence: successful renames copy up/redirect directory metadata and update context dentries. Repeated rename from the old source expects `ENOENT`.

Dependencies and integration: depends on overlayfs redirect_dir support unless xdev mode selects `rename-exdev` instead.

Risks: directory rename behavior differs when redirect_dir is disabled; terminal slash and nested paths affect errno.

Test signals: validates populated directory rename with contents preserved under new name.
