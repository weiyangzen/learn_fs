<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_utils.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_utils.py

Purpose: shared execution utilities for parallel and per-test coverage runners. It creates/checks build directories and dispatches tasks across process workers.

Important APIs: `PushWorkingDirectory` changes cwd and restores via `pop()`. `setup_run_tasks_parallel()` initializes each worker process by taking one build directory from a multiprocessing queue and `chdir`ing into it. `run_task_lists_in_parallel()` creates a `ProcessPoolExecutor`, submits all tasks, optionally checks results, and optionally collects timing data. `check_build_dirs()` validates that copied build directories contain compile-time `.gcno` files and logs runtime `.gcda` presence. `setup_build_dirs()` creates build_0, executes setup commands there, then copies it to the remaining build dirs.

State and persistence: creates and copies build directories; reads coverage files to validate state. It does not clean directories.

Dependencies and integration: imported by `parallel_code_coverage.py` and `per_test_code_coverage.py`. Depends on multiprocessing, subprocess, shutil, and command strings from config JSON.

Risks and test signals: `task.split()` is not shell-compatible quoting. `PushWorkingDirectory` is not exception-safe. Setup command failures are logged but not re-raised, so later missing `.gcno` checks may be the effective failure. Worker count equals number of build dirs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_utils.py -->
