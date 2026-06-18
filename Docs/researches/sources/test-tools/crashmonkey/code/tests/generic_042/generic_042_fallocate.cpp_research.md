# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate.cpp

Purpose: aligned plain `fallocate` variant of generic/042. It verifies that prewritten file data remains `0xff` after allocating an already-covered aligned range without zeroing or punching.

Important APIs/types/functions: `Generic042Fallocate`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, 0)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: the inherited run writes 64 KiB, calls `fallocate` with mode `0` at offset 60 KiB for 4 KiB, fsyncs, and checkpoints. `check_test()` first accepts empty-or-complete state via `CheckBase`; if complete, it checks the full 64 KiB for `0xff`.

State/persistence behavior: no zeros should be introduced, and file size should remain 64 KiB when the checkpoint has replayed.

Dependencies/integration: thin plugin wrapper around `Generic042Base` plus CrashMonkey factory functions.

Risks/test signals: detects stale or zeroed data in the full data range, but not block count changes. Signal is `kFileDataCorrupted` from base helpers.
