<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/333 -->
# sources/test-tools/xfstests/tests/btrfs/333

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/333_research.md`.

Source read: 235 lines, SHA256 prefix `c6b6498241bd5937`.

Purpose: FS QA Test No. btrfs/333 Test btrfs encoded reads.

Important APIs/types/functions: test tags `auto quick compress rw io_uring ioctl`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_command src/btrfs_encoded_read`, `_require_command src/btrfs_encoded_write`, `_require_btrfs_iouring_encoded_read`, `_require_btrfs_no_nodatacow`, `_require_btrfs_no_nodatasum`; helper functions `do_encoded_read()`, `do_encoded_write()`, `test_file()`; key variables `sector_size=$(_scratch_btrfs_sectorsize)`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `do_encoded_read()`, `do_encoded_write()`, `test_file()`. Representative operation sequence: L16: _require_btrfs_iouring_encoded_read; L20: _require_btrfs_no_nodatacow; L21: _require_btrfs_no_nodatasum; L82: local md5=`md5sum $datafile | cut -d ' ' -f 1`; L180: local md5=`md5sum $randfile | cut -d ' ' -f 1`; L198: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L199: sector_size=$(_scratch_btrfs_sectorsize); L203: _scratch_mount "-o max_inline=2048".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; visible subtest labels include btrfs encoded read failed with -EPERM; are you running as root?" \; btrfs encoded write failed with -EPERM; are you running as root?" \; Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/333 -->
