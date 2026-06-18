<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/818 -->
# sources/test-tools/xfstests/tests/xfs/818

Purpose: validates that `xfs_protofile` can describe a populated XFS tree, that mkfs can recreate it with `-p`, and that file metadata and content match.

Important APIs, types, and functions: defines `make_md5`, `cmp_md5`, `make_stat`, and `cmp_stat`; uses `_scratch_populate_cached`, `_run_fsstress`, `$XFS_PROTOFILE_PROG`, `_try_mkfs_dev -p`, and standard `find`, `stat`, `md5sum`, and `diff`.

Control flow: populate scratch, add fsstress-created files, record stats and hashes, generate a protofile, create a same-sized image, format it from the protofile, mount it, and compare stat and md5 data.

State and persistence behavior: creates a temporary image, protofile, and mount directory under `$TEST_DIR/$seq`; cleanup unmounts and removes them.

Dependencies and integration points: depends on xfs_protofile, mkfs protofile population, scrub/populate commands, and non-realtime compatibility.

Risks and test signals: known `_notrun` cases include too many xattr names, insufficient space from lost reflink sharing, and unsupported realtime files. Signals are clean stat diff and md5 verification.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/818 -->
