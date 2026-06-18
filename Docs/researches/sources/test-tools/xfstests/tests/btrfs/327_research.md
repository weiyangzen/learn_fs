<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/327 -->
# sources/test-tools/xfstests/tests/btrfs/327

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/327_research.md`.

Source read: 56 lines, SHA256 prefix `3684c7e1ca1bd9f6`.

Purpose: FS QA Test 327 Make sure reading inlined extents doesn't cause any corruption. This is a preventive test case inspired by btrfs/149, which can cause data corruption when the following out-of-tree patches are applied and the sector size is smaller than page size: btrfs: allow inline data extents creation if sector size < page size btrfs: allow buffered write to skip full page if it's sector aligned Thankfully no upstream kernel is affected..

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_support_sectorsize 4096`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L29: _require_btrfs_support_sectorsize 4096; L31: _scratch_mkfs >>$seqres.full 2>&1; L32: _scratch_mount "-o compress,max_inline=4095"; L39: $XFS_IO_PROG -f -c "pwrite 0 4k" "$SCRATCH_MNT/foobar" > /dev/null; L47: $XFS_IO_PROG -f -c "pwrite 8k 4k" "$SCRATCH_MNT/foobar" > /dev/null.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include 3 > /proc/sys/vm/drop_caches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/327 -->
