# sources/test-tools/ltp/testcases/kernel/fs/iso9660/Makefile

## Purpose

This Makefile installs the ISO9660 shell testcase rather than building a binary.

## Important APIs, Types, and Functions

It includes `testcases.mk`, sets `MAKE_TARGETS :=`, sets `INSTALL_TARGETS := isofs.sh`, and includes `generic_leaf_target.mk`.

## Control Flow

The generic leaf rules skip compilation and install only `isofs.sh`.

## State and Persistence Behavior

No runtime state is owned by the Makefile.

## Dependencies and Integration Points

Integrates the script into LTP's installed testcase set.

## Risks and Edge Cases

If helper data files are added, `INSTALL_TARGETS` must be updated. Empty `MAKE_TARGETS` is intentional.

## Test Signals

Install success for `isofs.sh` is the relevant signal.
