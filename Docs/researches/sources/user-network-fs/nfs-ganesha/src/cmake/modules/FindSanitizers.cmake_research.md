# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindSanitizers.cmake

## Purpose

`FindSanitizers.cmake` is the umbrella sanitizer module. It exposes static sanitizer runtime linking and imports ASan, TSan, MSan, and UBSan modules, then provides helpers to apply all enabled sanitizers to one or more targets.

## Important APIs, Types, and Functions

The public APIs are option `SANITIZE_LINK_STATIC`, function `sanitizer_add_blacklist_file(FILE)`, and function `add_sanitizers(...)`. It relies on `add_sanitize_address`, `add_sanitize_thread`, `add_sanitize_memory`, and `add_sanitize_undefined` from component modules.

## Control Flow

The module maps `Sanitizers_FIND_QUIETLY` to `FIND_QUIETLY_FLAG`, finds each component sanitizer package, and defines helper functions. `sanitizer_add_blacklist_file` resolves relative paths against `CMAKE_CURRENT_SOURCE_DIR` and probes `-fsanitize-blacklist=<file>`. `add_sanitizers` iterates over every target argument and invokes each enabled sanitizer's target function.

## State and Persistence Behavior

It stores detected sanitizer and blacklist flags in CMake cache variables managed by `sanitize-helpers.cmake`. Target compile/link flags are mutated only when `add_sanitizers` is called.

## Dependencies and Integration Points

It depends on component modules `FindASan`, `FindTSan`, `FindMSan`, `FindUBSan`, and `sanitize-helpers.cmake`. `config_parsing/CMakeLists.txt` uses `add_sanitizers(config_parsing)` and applies it to the RADOS URL module when built.

## Risks and Edge Cases

The module does not enforce sanitizer compatibility itself beyond component modules; users can still request combinations that fail at link/runtime. `-fsanitize-blacklist` has been renamed in newer Clang to ignorelist, so modern compilers may need updated flag candidates. Static sanitizer runtime linking is only attempted for GNU compilers in helper logic.

## Test Signals

Configure with each sanitizer option alone and in invalid combinations, then inspect target flags and build sanitized binaries. Runtime smoke tests should verify instrumented targets start and report sanitizer findings.
