<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/318 -->
# sources/test-tools/xfstests/tests/btrfs/318

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/318_research.md`.

Source read: 106 lines, SHA256 prefix `704df25a035adb9b`.

Purpose: FS QA Test No. 318 Test an edge case of multi device volume management in btrfs. If a device changes devt between mounts of a multi device fs, we can trick btrfs into mounting the same device twice fully (not as a bind mount). From there, it is trivial to induce corruption..

Important APIs/types/functions: test tags `auto quick volume scrub tempfsid`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 9f7eb8405dcb \`, `_require_test`, `_require_command "$PARTED_PROG" parted`, `_require_batched_discard "$TEST_DIR"`, `_require_loop`; helper functions `_cleanup()`; key variables `IMG0=$TEST_DIR/$$.img0`, `IMG1=$TEST_DIR/$$.img1`, `IMG2=$TEST_DIR/$$.img2`, `DEV0=$(_create_loop_device $IMG0)`, `DEV1=$(_create_loop_device $IMG1)`, `DEV2=$(_create_loop_device $IMG2)`, `D0P1=$DEV0"p1"`, `D1P1=$DEV1"p1"`, `MNT=$TEST_DIR/mnt-${seq}`, `BIND=$TEST_DIR/bind-${seq}`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L54: $MKFS_BTRFS_PROG -f -msingle -dsingle $D0P1 $DEV2 >>$seqres.full 2>&1 || _fail "failed to mkfs.btrfs"; L60: _mount $D0P1 $MNT; L70: _mount $D0P1 $MNT; L73: $BTRFS_UTIL_PROG device remove $DEV2 $MNT; L78: _mount $D0P1 $BIND; L79: mount_show=$($BTRFS_UTIL_PROG filesystem show $MNT); L80: bind_show=$($BTRFS_UTIL_PROG filesystem show $BIND); L86: $XFS_IO_PROG -f -c "pwrite 0 50M" $MNT/foo.$i >>$seqres.full 2>&1; L89: $XFS_IO_PROG -f -c "pwrite 0 50M" $BIND/foo.$i >>$seqres.full 2>&1; L103: $BTRFS_UTIL_PROG scrub start -B $MNT | grep "Error summary:".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates loop devices or image-backed devices; drops page cache to force media-backed reads.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: requires privileged cache dropping and can perturb the host; loop-device cleanup must run to avoid leaked devices; device identity and partition node timing are important; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: visible subtest labels include 3 > /proc/sys/vm/drop_caches.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/318 -->
