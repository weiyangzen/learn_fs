<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config_catch2.json -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config_catch2.json

Purpose: minimal coverage configuration for running only Catch2 unit tests under the same coverage harness used by broader coverage tasks.

Data contract: contains `_comments`, `setup_actions`, and `test_tasks`. Setup configures a coverage build with `cmake --preset linux-gcc`, unit tests enabled, diagnostics disabled, coverage instrumentation, inline-function flag, Coverage build type, and Ninja generator, then runs `ninja`. The sole test command is `test/catch2/catch2-unittests`.

State and persistence: creates instrumented build directories via the Python coverage runners. Runtime coverage files are emitted by Catch2 execution and collected by gcovr.

Dependencies and integration: used by Evergreen `coverage-report-catch2` and the coverage Python scripts. Requires the Catch2 target to be built and coverage flags to produce `.gcno`/`.gcda`.

Risks and test signals: the setup uses plain `ninja` rather than explicit `-j`, so runtime depends on Ninja defaults. The same command-splitting limitations apply as with the main coverage config. Failure signals come from setup command exit codes, Catch2 exit code, and missing coverage files detected by `check_build_dirs()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config_catch2.json -->
