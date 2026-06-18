<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/336 -->
# sources/test-tools/xfstests/tests/btrfs/336

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/336_research.md`.

Source read: 35 lines, SHA256 prefix `320c67fc478158d2`.

Purpose: FS QA Test 336 Make sure read-only scrub won't cause NULL pointer dereference with rescue=idatacsums mount option.

Important APIs/types/functions: test tags `auto scrub quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 6aecd91a5c5b \`, `_require_scratch`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _scratch_mkfs >> $seqres.full; L19: _try_scratch_mount "-o ro,rescue=ignoredatacsums" > /dev/null 2>&1 ||; L23: $BTRFS_UTIL_PROG scrub start -Br $SCRATCH_MNT >> $seqres.full 2>&1; L29: _scratch_unmount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include read-only scrub should fail but didn't; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/336 -->
