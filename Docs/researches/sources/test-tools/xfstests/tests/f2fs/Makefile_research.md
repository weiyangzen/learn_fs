# sources/test-tools/xfstests/tests/f2fs/Makefile

## Purpose

This Makefile is the install/build manifest for the xfstests `f2fs` test directory. It delegates to the shared `include/builddefs` and `$(BUILDRULES)` infrastructure and declares which numbered shell tests and companion files are part of this suite.

## Important APIs, Types, and Functions

The primary interface is GNU make metadata: `TOPDIR`, `include $(TOPDIR)/include/builddefs`, `TARGET_DIR`, `INSTALL_DIR`, `INSTALL_MODE`, `TESTS`, `MKFS_CONFIGS`, and `default: depend`. The `include $(BUILDRULES)` line supplies the common xfstests targets for dependency generation and installation.

## Control Flow

Make evaluates the top-level path variables, includes global build definitions, sets the destination directory to `$(PKG_LIB_DIR)/tests/f2fs`, lists tests/configuration payloads, and lets the shared build rules implement `default`, `depend`, and install behavior. The file does not run filesystem tests itself; it makes the scripts available to the harness.

## State and Persistence Behavior

Persistent output is limited to build/install artifacts produced by the shared Make rules. The manifest itself records 4 numbered test references; it has no runtime scratch-device state.

## Dependencies and Integration Points

It depends on the repository-level `include/builddefs` and `$(BUILDRULES)`. It integrates with xfstests packaging by installing the declared scripts under the suite-specific tests directory.

## Risks and Edge Cases

The main risk is manifest drift: adding or removing a test script without updating `TESTS` or `MKFS_CONFIGS` can prevent the harness from installing or discovering the intended file. Shared Make variables must be available from the top-level xfstests build environment.

## Test Signals

Useful signals are successful `make` dependency/install runs and the presence of every declared test/config in the installed `f2fs` tests directory.
