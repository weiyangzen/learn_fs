<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/CMakeLists.txt

Purpose: Top-level WiredTiger test directory CMake dispatcher.

Important APIs/types/functions: Adds common test subdirectories (`utility`, `checkpoint`, `cursor_order`, `fops`, `huge`, `manydbs`, `csuite`, `packing`), conditionally adds `catch2` under `HAVE_UNITTEST`, and POSIX-only suites under `WT_POSIX`. It also gates `cppsuite`, `model`, and LLVM fuzz tests.

Control flow: Configure-time platform and feature flags decide which test trees are compiled.

State and persistence behavior: No runtime state; creates build graph state in CMake.

Dependencies and integration points: Integrates WiredTiger test families with CMake feature variables such as `WT_WIN`, `WT_POSIX`, `ENABLE_CPPSUITE`, `ENABLE_MODEL`, and `ENABLE_LLVM`.

Risks and test signals: Platform gates can hide missing tests on Windows or non-POSIX builders. Configure checks should verify intended subdirectories are present for each build variant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/CMakeLists.txt -->
