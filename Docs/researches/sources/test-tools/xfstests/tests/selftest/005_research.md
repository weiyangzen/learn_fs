<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/005 -->
# sources/test-tools/xfstests/tests/selftest/005

## Purpose
Dangerous harness selftest that enables sysrq and triggers a kernel crash, used only to validate crash handling in controlled runner environments.

## Important APIs, Types, And Functions
`_begin_fstest dangerous_selftest` declares xfstests groups/tags: dangerous_selftest. Imports `common/preamble`.

## Control Flow
The test is a xfstests harness selftest. It follows xfstests shell flow: gate unsupported environments, create or format scratch/test media, execute targeted filesystem/tool operations, and report failure through golden-output differences, explicit diagnostics, or nonzero status. Notable source-derived steps: no imperative commands beyond harness declarations.

## State And Persistence
State is mostly external to the script. Temporary artifacts use `$tmp.*` and `$seqres.full`; filesystem state is created under scratch/test mount trees, loop devices, dm targets, tape devices, or package install directories depending on the test, and cleanup/unmount paths remove or isolate it.

## Dependencies And Integration Points
Integrates with xfstests common helpers for filtering, scratch setup, feature detection, cleanup, and subsystem-specific operations; the xfstests runner status, output comparison, crash, timeout, and flake handling paths.

## Risks And Test Signals
Risks: marked dangerous, so it can crash, hang, or exercise kernel failure paths; uses disruptive kernel/storage state such as cache dropping, shutdown, dm-error, error injection, or crash/hang triggers. Test signals: exit status and golden stdout comparison.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/selftest/005 -->
