# sources/test-tools/xfstests/tests/generic/619

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/619`. ENOSPC regression test in a multi-threaded scenario. Test allocation strategies of the file system and validate space anomalies as reported by the system versus the allocated by the program. The test is motivated by a bug in ext4 systems where-in ENOSPC is reported by the file system even though enough space for allocations is available[1]. [1]: https://patchwork.ozlabs.org/patch/1294003 Linux kernel patch series that fixes the above regression: 53f86b170dfa ("ext4: mballoc: add blocks to PA list under same spinlock after allocating blocks") cf5e2ca6c990 ("ext4: mballoc: refactor ext4_mb_discard_preallocations()") 07b5b8e1ac40 ("ext4: mballoc: introduce pcpu seqcnt for freeing PA to improve ENOSPC handling")... It is registered with `_begin_fstest auto rw enospc prealloc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 189 source line(s).
- Harness registration: `_begin_fstest auto rw enospc prealloc`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch`, `_require_test_program "t_enospc"`, `_require_xfs_io_command "falloc"`.
- Local shell functions: `debug`, `calc_thread_cnt`, `run_testcase`.
- External `$here/src` helpers: `$here/src/t_enospc -t $thread_cnt -s $file_ratio_unit -r $file_ratio -p $SCRATCH_MNT $extra_args >> $seqres.full`.
- Notable variables and constants:
- `FS_SIZE=$((240*1024*1024)) # 240MB`
- `DEBUG=1 # set to 0 to disable debug statements in shell and c-prog`
- `FACT=0.7`
- `FALLOCATE=1`
- `FTRUNCATE=2`
- `SMALL_FILE_SIZE=$((512 * 1024)) # in Bytes`
- `BIG_FILE_SIZE=$((1536 * 1024)) # in Bytes`
- `MIX_FILE_SIZE=$((2048 * 1024)) # (BIG + SMALL small file size)`
- `IFS=',' read -ra fratio <<< $file_ratio`
- `file_ratio_cnt=${#fratio[@]}`
- `tot_avail_size=$($DF_PROG --block-size=1 $SCRATCH_MNT | $AWK_PROG 'FNR == 2 { print $5 }')`
- `avail_size=$(echo $tot_avail_size*$disk_saturation | $BC_PROG)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_test_program "t_enospc"`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 53: echo "$1" >> $seqres.full`
- `line 83: echo ${thread_cnt}`
- `line 153: echo "FAIL: Aborted assertion faliure"`
- `line 156: echo "FAIL: ENOSPC BUS faliure"`
- `line 158: echo "$test_name failed at iteration count: $i"`
- `line 159: echo "$($DF_PROG -h $SCRATCH_MNT)"`
- `line 160: echo "Allocated: $alloc_per% Used: $use_per%"`
- `line 187: echo "Silence is golden"`
- Key operational lines include:
- `line 48: _require_xfs_io_command "falloc"`
- `line 134: _scratch_mkfs_sized $FS_SIZE >> $seqres.full 2>&1`
- `line 135: _scratch_mount`
- `line 166: _scratch_unmount`
- `line 175: "Small-file-fallocate-test:$SMALL_FILE_SIZE:1:$FACT:$FALLOCATE:3"`
- `line 176: "Big-file-fallocate-test:$BIG_FILE_SIZE:1:$FACT:$FALLOCATE:3"`
- `line 177: "Mix-file-fallocate-test:$MIX_FILE_SIZE:0.75,0.25:$FACT:$FALLOCATE:3"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw enospc prealloc`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/619.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_test_program "t_enospc"`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- ENOSPC-sensitive timing can vary with allocator geometry, free-space accounting, delayed allocation, and background reservations.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 619; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
