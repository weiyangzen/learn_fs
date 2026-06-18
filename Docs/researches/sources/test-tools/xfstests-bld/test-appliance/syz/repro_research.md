# sources/test-tools/xfstests-bld/test-appliance/syz/repro

Purpose: generic/template xfstests wrapper for a syzkaller reproducer named by the invoked script path.

Important flow: identical to `syz/001`: source xfstests common helpers, require scratch, mount scratch, run `$seqfull.exe` with timeout or `$seqfull.syz` through `run-syz`, otherwise `_notrun`.

State and dependencies: writes result files for the invoked sequence, uses scratch mount, and requires syzkaller executor for `.syz` inputs.

Integration points: can be copied or symlinked for new syzkaller repro cases.

Risks and test signals: path-derived `seq` and `seqfull` must match reproducer file naming. Kernel crashes or hangs are expected signals for repro tests, so harness and LTM timeout handling are important.
