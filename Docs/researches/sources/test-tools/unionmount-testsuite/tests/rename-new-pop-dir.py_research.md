# sources/test-tools/unionmount-testsuite/tests/rename-new-pop-dir.py

Purpose: exhaustively tests renaming newly created populated directories. It validates child preservation, replacement semantics, and behavior when lower directories have been removed, emptied, or left populated.

Important APIs and functions: nineteen `subtest_*` functions use `ctx.mkdir()`, `ctx.open_file()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.unlink()`, `ctx.rmtree()`, `ctx.open_dir()`, and errno expectations including `ENOENT`, `EISDIR`, `EINVAL`, `ENOTDIR`, and `ENOTEMPTY`.

Control flow: initial cases create a new directory containing `a`, rename it back and forth, attempt invalid unlinks/removes, and verify content. Later cases rename over empty dirs, removed lower dirs, removed populated lower dirs, same-name/different-name child layouts, and an emptied lower directory.

State and persistence: state includes upper-created directory trees and lower directory deletion markers. Child files such as `a`, `b`, and `pop/x` verify which tree survived after replacement.

Dependencies and integration: integrates with overlay whiteout/opaque handling and recursive removal via harness helpers. It assumes lower fixtures have a known `pop` subtree.

Risks: high coverage but high setup sensitivity; a fixture layout change can invalidate many hardcoded child checks. Rename-over-removed-lower cases are subtle across overlay modes.

Test signals: final directories must open at the target, source names must disappear where expected, and child contents or absences must match each scenario.
