# sources/test-tools/unionmount-testsuite/unmount_union.py

Purpose: central teardown helper for unmounting unionmount/overlay test filesystems and checking kernel taint after each unmount stage.

Important APIs and functions: exports `unmount_union(ctx)`. It imports `system` and `check_not_tainted` from `tool_box`.

Control flow: obtains `cfg = ctx.config()`, unmounts the union mount, optionally unmounts lower, overlay upper submounts, base, or upper mounts based on config predicates. Overlay upper child unmounts are attempted with a wildcard and ignored if they fail.

State and persistence: tears down real mounted filesystems. It does not persist local state, but it changes global mount namespace state and checks kernel taint after operations.

Dependencies and integration: depends on configuration methods such as `union_mntroot()`, `should_mount_lower()`, `testing_overlayfs()`, `maxfs()`, `is_nested()`, `upper_mntroot()`, `should_mount_base()`, and `should_mount_upper()`.

Risks: wildcard unmount command is shell-expanded and may behave unexpectedly if paths contain spaces. Ignoring upper child unmount failures may hide partial teardown problems until later stages.

Test signals: any unmount command failure outside the ignored wildcard path or any kernel taint change fails teardown.
