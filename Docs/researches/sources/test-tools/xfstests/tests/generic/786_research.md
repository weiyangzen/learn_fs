# sources/test-tools/xfstests/tests/generic/786


Purpose: Thin wrapper test for directory delegation support through the locktest common helpers.


Important APIs, helpers, and commands: Imports `common/locktest`; requires `_require_test_fcntl_setdeleg` and calls `_run_dirdelegtest`.
 It imports `./common/filter`, `./common/locktest`, `./common/preamble`.
 Capability gates include `_require_test`, `_require_test_fcntl_setdeleg`.



Control flow, state, dependencies, risks, and test signals: The control flow is capability gate then helper execution. State is whatever delegation locks the helper establishes in the test filesystem. Dependencies are fcntl delegation support and compiled locktest helpers. Risks are kernel/filesystem support gaps and helper-specific output. Success is helper exit 0. Source size is 19 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
