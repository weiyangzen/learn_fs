# sources/test-tools/unionmount-testsuite/tests/rename-hard-link.py

Purpose: verifies rename behavior for files that have hard links.

Important APIs/types/functions: single `subtest_1` using `ctx.link`, `ctx.rename`, and `ctx.open_file`.

Control flow: creates a hard link from a lower regular file to a new name, renames that linked name away and back, then renames the original source to a fourth name. Final checks ensure the original name is absent and the remaining linked names read the original content.

State and persistence: creates shared-inode dentries, then moves names while preserving content/inode association.

Dependencies and integration: relies on hardlink copy-up/index behavior and context rename/link inode tracking.

Risks: overlayfs without index support can have hardlink verification limitations in multi-layer modes.

Test signals: targets link-count/name preservation through rename operations.
