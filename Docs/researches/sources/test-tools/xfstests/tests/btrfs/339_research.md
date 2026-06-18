<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/339 -->
# sources/test-tools/xfstests/tests/btrfs/339

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/339_research.md`.

Source read: 32 lines, SHA256 prefix `a89b8cbbbda413db`.

Purpose: FS QA Test 339 Test btrfs receive dump stream from different user.

Important APIs/types/functions: test tags `auto quick send snapshot`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_user`; key variables `stream=$tmp.fsv.ss`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L21: _scratch_mount; L25: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap; L26: _btrfs send -f $stream $SCRATCH_MNT/snap; L28: _su $qa_user -c "$BTRFS_UTIL_PROG receive --dump -f $stream" >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/339 -->
