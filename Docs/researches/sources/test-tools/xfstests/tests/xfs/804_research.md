<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/804 -->
# sources/test-tools/xfstests/tests/xfs/804

Purpose: functional testing for the `xfs_property` wrapper across offline device mode and online mounted-directory mode.

Important APIs, types, and functions: uses `$XFS_PROPERTY_PROG` subcommands `get`, `set`, `list`, and `remove`, plus `attr -R -l` to observe backing filesystem property xattrs. Long property names and values are generated with perl.

Control flow: the script unmounts the test filesystem for offline device tests, then mounts it and repeats the same operation sequence online against `$TEST_DIR`.

State and persistence behavior: it creates and removes `fakeproperty`, temporary child paths, and no durable data beyond the filesystem property under test. Cleanup removes the property from `$TEST_DEV`.

Dependencies and integration points: depends on `xfs_property`, xattrs, test XFS, and `xfs_io listfsprops` as a feature probe.

Risks and test signals: risks include wrapper/device path divergence and incomplete cleanup. Signals are correct empty get/remove behavior, set/list/get visibility, and expected long input failures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/804 -->
