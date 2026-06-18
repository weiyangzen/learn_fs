<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/049 -->
# sources/test-tools/xfstests/tests/ext4/049

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/049_research.md`.

Source read: 51 lines, SHA256 prefix `1b655cd30fb270d5`.

Purpose: FS QA Test 049 Regression test for kernel commit a149d2a5cabb (ext4: fix check to prevent false positive report of incorrect used inodes) Import common functions..

Important APIs/types/functions: test tags `auto quick`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`; key variables `sdev=$(_short_dev ${SCRATCH_DEV})`, `sleep_time=5`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L25: _scratch_mkfs_ext4 -b 4096 -g 8192 -N 1024 -I 4096 >> $seqres.full 2>&1; L28: _scratch_mount -o errors=remount-ro; L46: _check_dmesg_for "\(${sdev}\): Remounting filesystem read-only" && \.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits.

Test signals: absence or presence of expected dmesg warnings; visible subtest labels include + create scratch fs; + mount fs; + check mountpoint status; + check mountpoint writability; + check dmesg; scratch dev should not be remounted to read-only.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/049 -->
