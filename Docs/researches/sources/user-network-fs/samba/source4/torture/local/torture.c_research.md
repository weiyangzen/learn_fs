# sources/user-network-fs/samba/source4/torture/local/torture.c

## Purpose
`torture.c` tests core smbtorture utility behavior: temporary directory creation and bare domain provisioning.

## Important APIs, types, and functions
`test_tempdir()` calls `torture_temp_dir()` and verifies `directory_exist()`. `test_provision()` builds a `provision_settings` struct and calls `provision_bare()`, then checks the returned domain DN. `torture_local_torture()` registers both tests.

## Control flow
The tempdir test requests a named temporary directory under the torture context. The provision test creates a temp target directory, fills domain/realm/site/machine settings, provisions a bare database, and validates `result.domaindn`.

## State and persistence behavior
Both tests create local filesystem state under temporary directories. The provision test creates a bare Samba provision tree/database in its temp target, owned by the test context.

## Dependencies and integration points
The file depends on raw SMB utility headers only lightly, `torture/util.h`, and `param/provision.h`. It is registered under the local smbtorture suite.

## Risks and edge cases
Provisioning depends on Python/build support and local filesystem permissions. Settings are minimal and use hard-coded domain values; failures can indicate provision code regressions rather than harness issues.

## Test signals
Passing tests show the torture harness can allocate temp directories and that bare provisioning produces the expected domain DN.
