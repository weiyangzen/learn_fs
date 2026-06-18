# sources/storage-engines/wiredtiger/test/csuite/CMakeLists.txt

Purpose: declares the WiredTiger `test/csuite` C test targets through the repository's `define_c_test` macro. It maps each csuite subdirectory to executable source files, arguments, smoke scripts, platform dependencies, additional files, labels, flags, and in one case C++ linker language.

Important APIs, types, and functions: the repeated build API is `define_c_test(TARGET ... SOURCES ... DIR_NAME ... EXEC_SCRIPT ... ARGUMENTS ... ADDITIONAL_FILES ... DEPENDS ... LABEL ... FLAGS ...)`. Targets in this subset include `test_normalized_pos`, `test_config`, `test_incr_backup`, `test_random`, `test_random_abort`, `test_random_directio`, `test_random_session`, and `test_rwlock`. The file also defines many other csuite targets such as timestamp, checkpoint, checksum, compact, schema, and disaggregated tests.

Control flow: CMake evaluates each `define_c_test` block during configure/generate. Blocks can attach POSIX gating through `DEPENDS "WT_POSIX"`, mark long-running or disaggregated tests via `LABEL`, pass generated target-file paths using generator expressions, and install/copy smoke scripts or companion scripts. The final block for `test_wt16990_disagg_checkpoint_panic` sets `LINKER_LANGUAGE CXX` when the target exists so sanitizer and extension runtimes link correctly.

State and persistence behavior: no runtime state is written by the CMake file itself, but it controls per-test build directories, copied scripts, `WT_HOME` argument locations, and whether targets enter CTest. The runtime tests create and remove their own WiredTiger homes under generated binary directories.

Dependencies and integration points: integrates csuite with the top-level WiredTiger CMake harness and `define_c_test`. It depends on target names matching source directories and smoke script paths. POSIX-dependent tests rely on `WT_POSIX`; direct-I/O, random abort, backup, and shell smoke scripts are gated accordingly.

Risks: target/source/script naming drift can silently break CTest registration. Long-running labels must stay accurate for sanitizer/buildbot scheduling. `test_random_directio` compiles both `main.c` and `util.c`; omitting helper sources would link-fail. Additional smoke scripts, such as LazyFS variants, must be listed to be available in build directories.

Test signals: CMake generation should create all requested targets, CTest should attach correct scripts/arguments/labels, and POSIX-gated targets should be omitted or disabled on unsupported platforms.
