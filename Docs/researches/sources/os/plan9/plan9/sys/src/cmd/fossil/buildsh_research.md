# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/buildsh

Plan 9 rc script for constructing a test namespace.

It mounts `ehime`, sets a test root, defines a local `bind` wrapper, binds terminal devices, the test root, kernel device filesystems, bin directories, and moves to `/sys/src` with a custom prompt before starting interactive `rc`.

This is an operator/developer helper, not part of the fossil runtime.
