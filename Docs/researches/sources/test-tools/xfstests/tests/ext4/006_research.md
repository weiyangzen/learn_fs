<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/006 -->
# sources/test-tools/xfstests/tests/ext4/006

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/006_research.md`.

Source read: 140 lines, SHA256 prefix `30dac6d3712a9ce2`.

Purpose: FS QA Test No. 006 Create and populate an ext4 filesystem, fuzz the metadata, then see how the kernel reacts, how e2fsck fares in fixing the mess, and then try more kernel accesses to see if it really fixed things. Override the default cleanup function..

Important APIs/types/functions: test tags `dangerous_fuzzers`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, `. ./common/populate`, `. ./common/fuzzy`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_attrs`, `_require_populate_commands`; helper functions `_cleanup()`, `repair_scratch()`; key variables `fsck_pass="$1"`, `FSCK_LOG="${tmp}-fuzz-${fsck_pass}.log"`, `SRCDIR=`pwd``, `BLK_SZ=4096`, `ROUND2_LOG="${tmp}-round2-${fsck_pass}.log"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `repair_scratch()`. Representative operation sequence: L43: e2fsck -f -y "${SCRATCH_DEV}"; L47: e2fsck -n "${SCRATCH_DEV}" >> "${FSCK_LOG}" 2>&1; L62: cmp -s "${tmp}-fuzz-$((fsck_pass - 1)).log" "${FSCK_LOG}"; L80: _scratch_mkfs_ext4 >> $seqres.full 2>&1; L83: _scratch_populate >> $seqres.full; L86: _check_scratch_fs >> $seqres.full 2>&1 || _fail "should pass initial fsck"; L92: _try_scratch_mount >> $seqres.full 2>&1; L95: _scratch_fuzz_test >> $seqres.full 2>&1; L98: _scratch_fuzz_modify >> $seqres.full 2>&1; L110: _check_scratch_fs >> $seqres.full 2>&1; L114: _try_scratch_mount >> $ROUND2_LOG 2>&1; L120: _scratch_fuzz_test >> $ROUND2_LOG 2>&1; L123: _scratch_fuzz_modify >> $ROUND2_LOG 2>&1; L131: _check_scratch_fs >> $seqres.full 2>&1; L133: grep -E -q '(did not fix|makes no progress)' $seqres.full && echo "e2fsck failed" | tee -a $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle; creates loop devices or image-backed devices.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: deliberately corrupts metadata and can trigger kernel failure paths; loop-device cleanup must run to avoid leaked devices.

Test signals: clean e2fsck verification; byte-for-byte compare of copied or restored data; visible subtest labels include ++ fsck makes no progress.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/006 -->
