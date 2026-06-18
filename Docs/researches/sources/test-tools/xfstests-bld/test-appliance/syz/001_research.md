# sources/test-tools/xfstests-bld/test-appliance/syz/001

Purpose: xfstests test case wrapper for a syzkaller reproducer named `001`.

Important flow: set standard xfstests variables, source `common/rc` and `common/filter`, install cleanup trap, require generic Linux scratch support, mount scratch, cd to scratch mount, then run either an executable reproducer `$here/$seqfull.exe` with 60-second timeout or a `.syz` program via `run-syz`; otherwise `_notrun`.

State and dependencies: writes `$RESULT_DIR/001` and `.full`, uses scratch filesystem, temp files, and xfstests status conventions. Depends on `syz-execprog` or executable reproducer.

Integration points: listed in `syz/group` and can be run by xfstests harness as group `syz`.

Risks and test signals: `seqfull=$0` means paths can include directories; the executable lookup uses `$here/$seqfull.exe`. Repro timeout kills the process but kernel side effects may persist. Test signal is harness pass/notrun/failure and `.full` output.
