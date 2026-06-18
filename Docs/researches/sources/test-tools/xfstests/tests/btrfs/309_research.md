<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/309 -->
# sources/test-tools/xfstests/tests/btrfs/309

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/309_research.md`.

Source read: 26 lines, SHA256 prefix `6c07800c04cd00c2`.

Purpose: FS QA Test 309 Try to snapshot a deleted subvolume..

Important APIs/types/functions: test tags `auto quick snapshot subvol`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_test_program t_snapshot_deleted_subvolume`, `_fixed_by_kernel_commit 7081929ab257 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L18: _scratch_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/309 -->
