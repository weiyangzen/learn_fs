<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/gvisor-smoke-test.sh -->
# sources/test-tools/syzkaller/tools/gvisor-smoke-test.sh

## Purpose

Runs a syz-manager smoke test in gVisor mode.

## Important APIs, Types, and Functions

mktemp config, optional `GVISOR_VMLINUX_PATH`, curl latest runsc, chmod/install, `sudo -E ./bin/syz-manager --mode smoke-test`.

## Control Flow

Creates temp workdir/config, obtains runsc as kernel image, then runs one-count gVisor VM smoke test; trap removes workdir.

## State and Persistence Behavior

Temporary workdir only, removed on exit.

## Dependencies and Integration Points

Requires built syz-manager, sudo, curl or local runsc, gVisor backend support.

## Risks and Edge Cases

Latest runsc is unpinned; network-disabled args limit coverage; cleanup uses sudo rm.

## Test Signals

Run with downloaded and local runsc and verify smoke-test success.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/gvisor-smoke-test.sh -->
