<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/347 -->
# sources/test-tools/xfstests/tests/btrfs/347

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/347_research.md`.

Source read: 66 lines, SHA256 prefix `b81a86da86bc9d6d`.

Purpose: FS QA Test 347 Test that using the received subvol ioctl to set a received UUID on a root does not trigger a transaction abort (and turn the filesystem to RO mode) if a user abuses by assigning the same received UUID to a large number of subvolumes..

Important APIs/types/functions: test tags `auto quick subvol`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_test_program t_btrfs_received_uuid_ioctl`, `_require_scratch`, `_require_btrfs_support_sectorsize 4096`, `_fixed_by_kernel_commit 87f2c46003fc \`; key variables `num_subvols=496`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L15: _require_test_program t_btrfs_received_uuid_ioctl; L17: _require_btrfs_support_sectorsize 4096; L23: _scratch_mkfs -n 4K >> $seqres.full 2>&1 || _fail "mkfs failed"; L24: _scratch_mount; L41: _btrfs subvolume create $SCRATCH_MNT/sv_$i; L45: $here/src/t_btrfs_received_uuid_ioctl \; L51: _btrfs subvolume create $SCRATCH_MNT/sv_last; L52: $here/src/t_btrfs_received_uuid_ioctl \; L62: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/347 -->
