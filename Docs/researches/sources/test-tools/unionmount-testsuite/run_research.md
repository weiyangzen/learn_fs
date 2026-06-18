# sources/test-tools/unionmount-testsuite/run

Purpose: main Python CLI for configuring, setting up, running, cleaning, and directly replaying unionmount/overlayfs tests.

Important APIs/types/functions: `show_format`, top-level argument parser, direct `--open-file`/`--<fsop>` dispatch, cleanup/setup flow, test list construction, feature detection, and subtest discovery/execution.

Control flow: creates `config`, handles direct one-off operations, cleans old mounts, parses mode (`--no`, `--ov`, `--ovov[=layers]`), optional fuse/samefs/maxfs/squashfs/erofs/xdev/xino/meta/verify/terminal-slash flags, auto-detects overlay module and mount options, optionally performs setup-only, builds the test list, and for each test/recycle lane creates a `test_context`, calls `set_up` and `mount_union`, imports `tests.<name>`, finds `subtest_*` functions, sorts them by source line, runs them, checks taint, and unmounts. At the end it leaves a fresh union mounted for interactive use.

State and persistence: mutates system mounts, lower/upper/base directories, kernel drop-caches/taint checks, and test files. CLI direct mode can mutate arbitrary provided paths.

Dependencies and integration: depends on root-capable mount/umount, overlayfs/fuse-overlayfs/kernel feature files, `settings`, `context`, setup/mount/unmount/remount helpers, `tool_box`, and Python test modules.

Risks: string-built shell commands require trusted paths; imports execute test module top-level code; final remount leaves state behind by design; feature auto-enabling can change mount options from user input.

Test signals: the script is the suite driver; successful run means all selected subtests completed and the kernel remained untainted.
