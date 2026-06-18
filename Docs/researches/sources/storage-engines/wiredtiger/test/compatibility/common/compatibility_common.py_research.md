# sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_common.py

Purpose: Provides common path, clone, build, and subprocess helpers for the Python compatibility suite.

Important APIs/types/functions: `branch_path` resolves either `this` or a checked-out branch under `COMPATIBILITY_TEST`; `branch_build_path` derives a deterministic build directory and appends sanitized build-config keys; `system` raises on nonzero shell command exit; `prepare_branch` clones/pulls a branch, validates supported build config keys, copies current `CMakePresets.json`, selects `linux-gcc` or `linux-v4-gcc`, configures CMake/Ninja, and builds.

Control flow: module import establishes `TEST_DIR`, `DIST_TOP_DIR`, and Python/third-party paths without importing `wiredtiger`. `prepare_branch` optionally clones, interprets `standalone`, creates a build directory if no Ninja build exists, then runs `ninja` every time.

State and persistence: persistent state is the branch checkout and build tree on disk. Build directory names encode configuration, avoiding collisions between standalone and non-standalone builds.

Dependencies/integration: imports branch metadata from `compatibility_config`, uses `test_util.setup_3rdparty_paths`, shells out to `git`, `cmake`, and `ninja`, and is called by `compatibility_test.prepare_tests`.

Risks and test signals: shell-string command construction requires sanitized build config values and quoted paths; only CMake-era branches are supported here. Failures surface as raised exceptions from `system` or unsupported config keys, before compatibility tests run.
