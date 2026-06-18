# sources/user-network-fs/pyfuse3/test/pytest.ini

Purpose: Stores pytest default options and marker declarations for pyfuse3 tests.

Important APIs/types/functions: Sets `addopts = --verbose --assert=rewrite --tb=native -x` and declares marker `uses_fuse`.

Control flow: Pytest reads this during configuration. `-x` stops the run on first failure, and native tracebacks make debugging extension/FUSE failures clearer.

State and persistence: Persistent test policy only; no runtime state.

Dependencies and integration points: Integrates with tests using `pytestmark = fuse_test_marker()` and the custom checklogs plugin.

Risks: `-x` can hide later failures in full-suite runs. The marker must stay declared to avoid strict-marker warnings if enabled elsewhere.

Test signals: Applies to all pytest invocations rooted in the test directory.
