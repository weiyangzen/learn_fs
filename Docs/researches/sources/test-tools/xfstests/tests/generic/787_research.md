# sources/test-tools/xfstests/tests/generic/787


Purpose: Thin wrapper test for file delegation support through locktest helpers.


Important APIs, helpers, and commands: Imports `common/locktest`; requires `_require_test_fcntl_setdeleg` and calls `_run_filedelegtest`.
 It imports `./common/filter`, `./common/locktest`, `./common/preamble`.
 Capability gates include `_require_test`, `_require_test_fcntl_setdeleg`.



Control flow, state, dependencies, risks, and test signals: The script delegates all behavior to the file delegation helper after checking support. State is file delegation/lease state in the kernel. Dependencies are fcntl delegation support. Risks are support being experimental and helper output changes. Signal is helper success. Source size is 20 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
