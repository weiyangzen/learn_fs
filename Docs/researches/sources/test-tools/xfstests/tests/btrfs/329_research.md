<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/329 -->
# sources/test-tools/xfstests/tests/btrfs/329

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/329_research.md`.

Source read: 21 lines, SHA256 prefix `ca56834329e887ea`.

Purpose: FS QA Test 329 Verify sysfs knob input syntax for read_policy round-robin.

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/sysfs`, `. ./common/filter`; requirements/fixed gates `_require_test`, `_require_fs_sysfs_attr_policy $TEST_DEV read_policy round-robin`.

Control flow: The script is mostly straight-line after harness setup. The main operation is encoded through the xfstests helpers and shell builtins.

State and persistence behavior: mainly drives transient test files under TEST_DIR or SCRATCH_MNT.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/329 -->
