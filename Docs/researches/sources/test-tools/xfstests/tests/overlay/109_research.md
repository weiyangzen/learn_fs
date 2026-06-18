<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/109 -->
# sources/test-tools/xfstests/tests/overlay/109

## Purpose
Runs the unionmount testsuite against overlayfs for the all-unique/tmpfs topology with xino enabled. The script is intentionally small: it registers unionmount cleanup, gates on scratch/test/tmpfs requirements as needed, and delegates behavioral coverage to `_unionmount_testsuite_run` with topology-specific flags.

## Important APIs, Types, And Functions
`_begin_fstest auto union rotate nonsamefs xino` declares xfstests groups/tags: auto, union, rotate, nonsamefs, xino. Imports `common/preamble`, `common/filter`. Feature gates/fix annotations include `_register_cleanup`, `_require_extra_fs`, `_require_test`, `_require_scratch`, `_require_unionmount_testsuite`. External helper programs used include `unionmount`.

## Control Flow
The test is a overlay unionmount suite wrapper. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; overlayfs layer directories, mount options, xattrs, and scratch/test filesystem capabilities.

## Risks And Test Signals
Risks: main risk is environmental: missing helper binaries, unsupported mount options, insufficient scratch space, or expected-output drift. Test signals: quiet success usually prints `Silence is golden`.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/overlay/109 -->
