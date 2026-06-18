<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/337 -->
# sources/test-tools/xfstests/tests/btrfs/337

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/337_research.md`.

Source read: 53 lines, SHA256 prefix `632c209d0644be06`.

Purpose: FS QA Test 337 Test compressed read with shared extents, especially for bs < ps cases..

Important APIs/types/functions: test tags `auto quick compress clone`; common harness imports `. ./common/preamble`, `. ./common/reflink`; requirements/fixed gates `_fixed_by_kernel_commit 9786531399a6 \`, `_require_btrfs_support_sectorsize 4096`, `_require_scratch_reflink`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L17: _require_btrfs_support_sectorsize 4096; L18: _require_scratch_reflink; L22: _scratch_mkfs -s 4k >> $seqres.full || _fail "make a btrfs with -s 4k"; L23: _scratch_mount "-o compress"; L26: $XFS_IO_PROG -f -c "pwrite -S 0x0f 0 32K" \; L37: $XFS_IO_PROG -f -c "reflink $SCRATCH_MNT/base 32K 0 32K" \; L46: _scratch_cycle_mount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: visible subtest labels include Reflink source:; Before mount cycle:; After mount cycle:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/337 -->
