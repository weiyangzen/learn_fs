<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/345 -->
# sources/test-tools/xfstests/tests/btrfs/345

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/345_research.md`.

Source read: 73 lines, SHA256 prefix `4844a985a6e23c7d`.

Purpose: FS QA Test 345 Test that we can create a large number of snapshots of a received subvolume without triggering a transaction abort due to leaf item overflow. Also check that we are able to delete the snapshots and use the last one for an incremental send/receive despite an item overflow when updating the uuid tree to insert a BTRFS_UUID_KEY_RECEIVED_SUBVOL item..

Important APIs/types/functions: test tags `auto quick subvol send snapshot`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_support_sectorsize 4096`, `_require_btrfs_command "property"`, `_fixed_by_kernel_commit e1b18b959025 \`; key variables `total=$(( 1000 * LOAD_FACTOR ))`, `last_snap="${SCRATCH_MNT}/snaps/sv_${total}"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _require_btrfs_support_sectorsize 4096; L18: _require_btrfs_command "property"; L24: _scratch_mkfs -n 4K >> $seqres.full 2>&1 || _fail "mkfs failed"; L25: _scratch_mount; L28: _btrfs subvolume create $SCRATCH_MNT/sv; L32: _btrfs property set $SCRATCH_MNT/sv ro true; L38: _btrfs send -f $SCRATCH_MNT/send.stream $SCRATCH_MNT/sv; L39: _btrfs receive -f $SCRATCH_MNT/send.stream $SCRATCH_MNT/snaps; L46: _btrfs subvolume snapshot -r $SCRATCH_MNT/snaps/sv $SCRATCH_MNT/snaps/sv_$i; L52: _btrfs subvolume snapshot $last_snap $SCRATCH_MNT/snaps/sv_last_as_parent; L54: _btrfs property set $SCRATCH_MNT/snaps/sv_last_as_parent ro true; L59: _btrfs send -f $SCRATCH_MNT/inc_send.stream -p $last_snap \; L61: _btrfs receive -f $SCRATCH_MNT/inc_send.stream $SCRATCH_MNT/; L64: diff $SCRATCH_MNT/snaps/sv_last_as_parent/bar $SCRATCH_MNT/sv_last_as_parent/bar; L68: _btrfs subvolume delete $SCRATCH_MNT/snaps/sv_$i.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: runtime and object count scale with the harness load factor; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; byte-for-byte compare of copied or restored data; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/345 -->
