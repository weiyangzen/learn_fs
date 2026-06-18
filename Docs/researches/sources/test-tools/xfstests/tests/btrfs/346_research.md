<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/346 -->
# sources/test-tools/xfstests/tests/btrfs/346

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/346_research.md`.

Source read: 95 lines, SHA256 prefix `cd6c498889f7b8b0`.

Purpose: FS QA Test 346 Test that if we create a high number of files with a name that results in a hash collision, the filesystem is not turned to RO due to a transaction abort. This could be exploited by malicious users to disrupt a system..

Important APIs/types/functions: test tags `auto quick subvol`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_support_sectorsize 4096`, `_fixed_by_kernel_commit 2d1ababdedd4 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L15: _require_btrfs_support_sectorsize 4096; L22: _scratch_mkfs -n 4K >> $seqres.full 2>&1 || _fail "mkfs failed"; L23: _scratch_mount; L76: _scratch_cycle_mount; L82: $BTRFS_UTIL_PROG subvolume create \; L92: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/346 -->
