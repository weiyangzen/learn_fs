# sources/test-tools/xfstests/tests/generic/759


Purpose: Runs fsx with userspace buffers backed by transparent huge pages to stress buffered read/write paths.


Important APIs, helpers, and commands: Uses `_require_thp`, `_require_hugepage_fsx`, and `_run_hugepage_fsx` with varied operation offsets.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_hugepage_fsx`, `_require_test`, `_require_thp`.



Control flow, state, dependencies, risks, and test signals: The control flow is three fsx runs of 10000 operations and 500000-byte maximum length, with offsets 0, 8192, and 128000. State is fsx-generated test files in the test area and THP-backed user buffers. Dependencies are THP and the hugepage fsx helper. Risks are nondeterminism and THP allocation availability. Success is fsx completing without data model mismatch. Source size is 23 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
