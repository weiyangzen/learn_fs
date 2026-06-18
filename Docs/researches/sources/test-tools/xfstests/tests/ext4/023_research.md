<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/023 -->
# sources/test-tools/xfstests/tests/ext4/023

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/023_research.md`.

Source read: 34 lines, SHA256 prefix `dd2bcedac4a0d644`.

Purpose: FS QA Test No. 023 Ensure that the populate helpers actually /can/ populate a ext4 filesystem with all types of metadata and create an image of the metadata. Check that fsck is happy with the resulting fs..

Important APIs/types/functions: test tags `auto quick scrub`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/populate`, `. ./common/fuzzy`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L27: _scratch_populate_cached > $seqres.full 2>&1; L30: _scratch_mount >> $seqres.full 2>&1.

State and persistence behavior: mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Format and populate; Mount.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/023 -->
