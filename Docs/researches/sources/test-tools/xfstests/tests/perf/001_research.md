<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/001 -->
# sources/test-tools/xfstests/tests/perf/001

## Purpose
Buffered random-write performance benchmark. It generates a fio psync randwrite job sized by `LOAD_FACTOR`, verifies the scratch filesystem has enough capacity, captures JSON fio output, and compares the result through xfstests performance helpers.

## Important APIs, Types, And Functions
`_begin_fstest auto` declares xfstests groups/tags: auto. Imports `common/preamble`, `common/filter`, `common/perf`. Feature gates/fix annotations include `_require_scratch`, `_require_block_device`, `_require_fio_results`, `_require_fio`, `_require_fs_space`. External helper programs used include `fio`, `$FIO_PROG`.

## Control Flow
The test is a xfstests performance benchmark. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 42: `_scratch_mkfs >> $seqres.full 2>&1`; line 43: `_scratch_mount`; line 47: `$FIO_PROG --output-format=json --output=$fio_results $fio_config`; line 49: `_scratch_unmount`.

## State And Persistence
State is kept in shell variables such as `fio_config`, `fio_results`, `_size`, `directory`, `allrandrepeat`, `readwrite`, `size`, `ioengine`, `end_fsync`, `fallocate`. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; fio plus xfstests performance result initialization and comparison helpers.

## Risks And Test Signals
Risks: space/quota tests are sensitive to scratch capacity, mkfs geometry, and background reclaim. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/001 -->
