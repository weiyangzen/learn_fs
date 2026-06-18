# sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/smoke.sh

Purpose: this wrapper runs the WT-10461 skip list stress binary as a smoke test.

Important APIs and variables: it uses POSIX `sh`, `set -e`, optional positional binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default binary name is `wt10461_skip_list_stress`.

Control flow: it resolves the binary and executes a single wrapped invocation. The duration and workload are controlled by the C program, which loops internally for roughly fifteen minutes.

State and persistence behavior: the shell script owns no state. Each C test iteration creates and removes its own WiredTiger home.

Dependencies and integration points: it relies on the build system naming this binary without a `test_` prefix, unlike many other csuite wrappers. It is intended to be called by `make check` or a targeted test suite.

Risks and test signals: because the binary is time-based and CPU-parallel, runtime can be long. The only wrapper-level signal is nonzero exit if the binary asserts, crashes, or returns failure.
