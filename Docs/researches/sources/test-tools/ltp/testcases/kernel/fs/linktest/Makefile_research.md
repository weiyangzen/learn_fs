# sources/test-tools/ltp/testcases/kernel/fs/linktest/Makefile

## Purpose

This Makefile installs the shell-based hard-link and symlink count regression test.

## Important APIs, Types, and Functions

It includes `env_pre.mk`, sets `INSTALL_TARGETS := linktest.sh`, and includes `generic_leaf_target.mk`.

## Control Flow

No compilation occurs; generic leaf rules install the script.

## State and Persistence Behavior

No runtime state is owned by the Makefile.

## Dependencies and Integration Points

Integrates `linktest.sh` into LTP's installed test scripts.

## Risks and Edge Cases

If converted to modern `testcases.mk`, install behavior should be preserved. Additional helper scripts would need explicit install targets.

## Test Signals

Install success for `linktest.sh` is the relevant signal.
