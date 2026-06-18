<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/udf/102 -->
# sources/test-tools/xfstests/tests/udf/102

## Purpose
UDF mkfs/check test derived from UDFQA. It prepares a UDF scratch directory/device and runs the UDF filesystem checker against the scratch device.

## Important APIs, Types, And Functions
`_begin_fstest udf` declares xfstests groups/tags: udf. Imports `common/preamble`, `common/filter`. Local helpers: `_cleanup()`. Feature gates/fix annotations include `_require_scratch`.

## Control Flow
The test is a UDF filesystem utility test. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: line 16: `rm -f $tmp.*`; line 26: `_check_udf_filesystem $SCRATCH_DEV`.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; UDF scratch setup plus mkfs/check utilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/udf/102 -->
