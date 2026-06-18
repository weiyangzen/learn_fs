<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/cifs/001 -->
# sources/test-tools/xfstests/tests/cifs/001

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/cifs/001_research.md`.

Source read: 43 lines, SHA256 prefix `e625e6eb69c95677`.

Purpose: FS QA Test No. cifs/001 Sanity test for server-side copies initiated via CIFS_IOC_COPYCHUNK_FILE Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_cloner`, `_require_test`; helper functions `_cleanup()`; key variables `len=$(($i * 1024))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L31: $XFS_IO_PROG -f -c "pwrite -S $i 0 $len" $TEST_DIR/$$/src/${i} \; L38: $CLONER_PROG $TEST_DIR/$$/src/${i} $TEST_DIR/$$/dest/${i}; L39: diff $TEST_DIR/$$/src/${i} $TEST_DIR/$$/dest/${i}.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, xfs_io workload commands, CIFS/SMB clone helper. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: byte-for-byte compare of copied or restored data.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/cifs/001 -->
