<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/324 -->
# sources/test-tools/xfstests/tests/btrfs/324

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/324_research.md`.

Source read: 39 lines, SHA256 prefix `0edb3126cdb7de9f`.

Purpose: Test that remounting with the "compress" mount option clears the "compress-force" mount option previously specified..

Important APIs/types/functions: test tags `auto quick mount remount compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_fixed_by_kernel_commit 3510e684b8f6 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"; L17: _scratch_mount -o compress-force=zlib:9; L28: _scratch_remount compress=zlib:4.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; mount/statfs option visibility; visible subtest labels include compress-force not set to zlib:9 after initial mount:; compress not set to zlib:4 after remount:; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/324 -->
