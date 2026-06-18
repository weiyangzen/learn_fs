# sources/user-network-fs/pyfuse3/test/test_rounding.py

Purpose: Regression test for nanosecond timestamp round-trip precision in `EntryAttributes`.

Important APIs/types/functions: `test_rounding` uses `_NANOS_PER_SEC` and `EntryAttributes`, sets `st_atime_ns`, `st_ctime_ns`, and `st_mtime_ns` to a large value ending at maximum nanosecond offset, and asserts exact equality on readback.

Control flow: Constructs one native-backed attribute object and performs direct property assignment/readback with no FUSE mount.

State and persistence: No persistent state.

Dependencies and integration points: Depends on pyfuse3 native attribute property setters/getters.

Risks: Only covers dates near 2037 and deliberately skips y2038 and BSD/macOS birthtime coverage. It detects conversion rounding but not filesystem/kernel timestamp truncation.

Test signals: Direct signal that Python-facing nanosecond properties do not lose precision due to float division or conversion bugs.
