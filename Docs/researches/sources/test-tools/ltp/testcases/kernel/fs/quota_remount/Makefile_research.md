# sources/test-tools/ltp/testcases/kernel/fs/quota_remount/Makefile

## Purpose

This Makefile installs the quota remount shell testcase.

## Important APIs, Types, and Functions

It includes `testcases.mk`, sets `INSTALL_TARGETS := quota_remount_test01.sh`, and includes `generic_leaf_target.mk`.

## Control Flow

The generic leaf target installs the script without compiling local binaries.

## State and Persistence Behavior

No runtime state is owned by the Makefile.

## Dependencies and Integration Points

Integrates `quota_remount_test01.sh` into the LTP installed testcase tree.

## Risks and Edge Cases

Additional helper files would need explicit install entries.

## Test Signals

Install success for `quota_remount_test01.sh` is the relevant signal.
