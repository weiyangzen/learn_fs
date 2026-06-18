## sources/sync-backup/rsync/testsuite/safe-links-absolute-intree_test.py

Purpose: documents and tests that `--safe-links` classifies symlink safety by literal target text, so absolute symlinks are dropped even when they resolve inside the copied tree.

Important APIs and control flow: creates `from/linked_file`, an absolute symlink to it, and a relative symlink to the same file. It first verifies plain `-a` preserves both links. Then `-av --safe-links` must emit `ignoring unsafe symlink`, omit the absolute link, preserve the relative link, and copy the referent. Finally `--copy-unsafe-links` must materialize the absolute link as a regular file while preserving the relative link.

State and dependencies: changes cwd to `TMPDIR`, uses local helper assertions built on `is_a_link`, `os.readlink`, and `os.path`.

Integration points: covers `unsafe_symlink()` policy and safe/copy-unsafe link options.

Risks and test signals: exact stderr substring and filesystem type checks distinguish dropping from dereferencing. It intentionally encodes surprising but documented behavior.
