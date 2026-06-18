# sources/user-network-fs/bazil-fuse/options_helper_test.go

Purpose: This test-only helper exposes a way for tests to inject arbitrary mount option key/value pairs that the public safe API would normally prevent.

Important APIs, types, and functions: `ForTestSetMountOption(k, v string) MountOption` returns a mount option closure that writes `conf.options[k] = v`.

Control flow: Tests can pass this option to `Mount`; when options are applied, the raw key/value is inserted into the mount config.

State and persistence behavior: Transient test mount configuration only.

Dependencies and integration points: It is in package `fuse`, not `fuse_test`, so it can access private `mountConfig`. The lint ignore documents that the helper is used by tests such as a comma-error test outside this file's visible subset.

Risks: This bypasses validation and can produce mount helper errors. It is correctly scoped to `_test.go`.

Test signals: Its presence indicates option serialization has edge cases that require deliberate unsafe injection for coverage.
