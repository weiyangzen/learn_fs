<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/806 -->
# sources/test-tools/xfstests/tests/xfs/806

Purpose: checks that `mkfs.xfs` autofsck filesystem properties are visible to `xfs_scrub -o autofsck` and influence the scrub tool's reported directive.

Important APIs, types, and functions: uses `testme`, `mkfs.xfs -m <autofsck option>`, loop mounting, `XFS_SCRUB_PHASE=7`, and `$XFS_SCRUB_PROG -d -o autofsck`.

Control flow: a temporary 10 GiB image is reformatted for each autofsck value, mounted via loop, queried with xfs_scrub, filtered to directive output, and unmounted.

State and persistence behavior: state is confined to the sparse image and temporary mount directory. Each iteration rewrites the filesystem image.

Dependencies and integration points: depends on xfs_scrub, xfs_db attr_get support, loop mounts, fs property support, and xfstests fuzzy filtering.

Risks and test signals: absence of an autofsck directive is not tested because defaults vary with mkfs features. The signal is scrub reporting the expected directive text without path noise.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/806 -->
