# sources/storage-engines/wiredtiger/cmake/strict/strict_flags_helpers.cmake

Purpose: defines CMake helper functions that centralize strict compiler diagnostic flags for WiredTiger builds. `get_gnu_base_flags`, `get_clang_base_flags`, and `get_cl_base_flags` parse exactly one language selector (`C` or `CXX`), choose the matching CMake compiler version variable, build a list of warning/error flags, and return it through a parent-scope output variable.

Important APIs and control flow: each function uses `cmake_parse_arguments(PARSE_ARGV ...)`, rejects unknown arguments, rejects simultaneous C and CXX selection, and emits `message(FATAL_ERROR)` on missing language. GNU flags include `-Werror` plus version-gated warnings from GCC 5 through 8, with selected `-Wno-*` relaxations. Clang flags mostly suppress diagnostics incompatible with existing WiredTiger code or platforms, with Darwin-specific and version-specific exceptions. MSVC uses `/WX`, `/we4100`, and `/GS`.

State and dependencies: no persistent state is written. Integration depends on `CMAKE_C_COMPILER_VERSION`, `CMAKE_CXX_COMPILER_VERSION`, `WT_DARWIN`, and consumers applying the returned flag list, typically through diagnostic CMake variables.

Risks: unquoted `if(${...})` conditions assume parse variables are always defined as boolean-like strings. Compiler version comparisons can silently skip flags for vendor-specific version schemes. Relaxations such as reserved identifier suppressions are intentional technical debt tied to WT-11788.

Test signals: configure-time failure paths catch malformed helper use. Build matrix coverage across GCC, Clang, Apple Clang, Darwin, and MSVC is the meaningful validation signal.
