# sources/test-tools/ltp/testcases/kernel/fs/racer/Makefile

## Purpose

This Makefile installs the shell scripts for the filesystem racer stress suite.

## Important APIs, Types, and Functions

It sets `top_srcdir`, includes `testcases.mk`, sets `INSTALL_TARGETS := *.sh`, and includes `generic_leaf_target.mk`.

## Control Flow

The generic LTP leaf target installs all shell scripts in the directory, including the main racer driver and helper operation scripts.

## State and Persistence Behavior

No runtime state is owned by this Makefile; installed scripts create runtime state when executed.

## Dependencies and Integration Points

Integrates the `racer` shell suite into LTP as a script-only testcase directory.

## Risks and Edge Cases

The wildcard install target can include unintended shell files if added to the directory. It also means missing helper scripts are detected only by install/runtime coverage, not explicit target names.

## Test Signals

Install success for all `*.sh` racer scripts is the primary signal.
