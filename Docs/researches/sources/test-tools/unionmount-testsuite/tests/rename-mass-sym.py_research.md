# sources/test-tools/unionmount-testsuite/tests/rename-mass-sym.py

Purpose: stress-tests repeated circular renames of symlinks to files and symlinks to directories. It verifies both symlink object movement and target resolution after mass rename.

Important APIs and functions: six subtests use `ctx.direct_sym()`, `ctx.direct_dir_sym()`, `ctx.rename()`, `ctx.readlink()`, `ctx.open_file()`, `ctx.open_dir()`, `ctx.unlink()`, and `ctx.rmdir(..., err=ENOTDIR)`.

Control flow: subtests 1 to 3 rotate file symlinks, verify final link targets and readable file contents, then unlink them. Subtests 4 to 6 repeat for directory symlinks, verifying `readlink` target strings and openability as directories.

State and persistence: persistent state is the symlink inode/dentry mapping and link text. The test tracks only ring-position arithmetic locally.

Dependencies and integration: uses unionmount fixtures that provide numbered direct symlinks and directory symlinks. It exercises VFS symlink rename semantics through the overlay/union layer.

Risks: trailing slash mode changes behavior for operations through symlinks; the test explicitly checks directory symlink unlink by confirming `rmdir` returns `ENOTDIR`.

Test signals: expected link text, successful target opens, one missing gap, and no unexpected symlink leftovers after cleanup.
