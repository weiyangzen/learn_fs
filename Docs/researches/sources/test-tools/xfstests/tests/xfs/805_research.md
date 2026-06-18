<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/805 -->
# sources/test-tools/xfstests/tests/xfs/805

Purpose: verifies that `mkfs.xfs -m autofsck` encodes the requested automatic fsck directive as a filesystem property.

Important APIs, types, and functions: `testme` builds `mkfs.xfs -f -m autofsck[=value]` arguments for empty, named, and numeric values, then inspects root metadata with `xfs_db -x -c 'path /' -c 'attr_get -Z autofsck'`.

Control flow: the test creates a 10 GiB sparse image in `$TEST_DIR`, formats it repeatedly with different autofsck values, and prints the stored root property through xfs_db.

State and persistence behavior: all state is in the temporary sparse file and mount directory, removed during cleanup. No mounted filesystem is required for the assertions.

Dependencies and integration points: depends on `mkfs.xfs`, xfs_db attr_get support, and `xfs_io listfsprops` as the fs property feature probe.

Risks and test signals: unsupported mkfs options cause `_notrun`. The test signal is the exact property value stored by mkfs for each accepted spelling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/805 -->
