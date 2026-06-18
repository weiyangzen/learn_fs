<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/328 -->
# sources/test-tools/xfstests/tests/btrfs/328

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/328_research.md`.

Source read: 31 lines, SHA256 prefix `15998e3fcf20b951`.

Purpose: FS QA Test 328 Test that if we enable simple quotas on a filesystem and unmount it right after without doing any other changes to the filesystem, we are able to mount again the filesystem..

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit f2363e6fcc79 \`, `_require_scratch_enable_simple_quota`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _require_scratch_enable_simple_quota; L19: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L20: _scratch_mount; L22: $BTRFS_UTIL_PROG quota enable --simple $SCRATCH_MNT; L27: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/328 -->
