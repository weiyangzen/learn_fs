# sources/test-tools/unionmount-testsuite/mount_union.py

Purpose: constructs the union mount under test for either bind-mounted `--no` mode or overlay/fuse-overlay/nested overlay mode.

Important APIs/types/functions: `mount_union(ctx)`.

Control flow: for `--no`, it bind mounts the lower root onto the union mount and records upper-like device IDs. For overlay modes, it mounts or prepares the upper root, creates the current layer directory with `u` and `w`, optionally mounts a per-layer tmpfs, writes a pure upper file, optionally mounts a nested overlay as the lower layer, then mounts the tested overlay/fuse filesystem with lowerdir/upperdir/workdir and configured mount options. It records lower layers, upper layer path, and device IDs for later checks.

State and persistence: creates directories under upper/base roots, mounts tmpfs and overlay filesystems, and writes `upperdir/f` as a pure upper sample.

Dependencies and integration: depends on `tool_box.system`, `write_file`, `config`, and `test_context` note methods. Called by `run` after `set_up`.

Risks: shell command construction is string-based; leftover upper contents are removed with `rm -rf`; mount failures are fatal; nested mount option adjustments are policy-heavy.

Test signals: all non-direct suite runs depend on successful mount and correct recorded device/layer metadata.
