# sources/storage-engines/wiredtiger/cmake/configs/base.cmake

## Purpose
`base.cmake` defines WiredTiger's central build configuration options and default values. It chooses defaults from build type, platform, and discovered libraries, exposes cache options through helper macros, and applies derived flag/config relationships.

## Important APIs, Types, And Functions
It uses `config_choice`, `config_bool`, and `config_string` from `helpers.cmake` to define architecture, OS, diagnostics, error logging, ref tracking, call log, unit tests, coverage, static/shared builds, PIC, strict mode, Python/SWIG, spinlock type, compression/encryption/storage extensions, cppsuite/model/PALite/LazyFS/LLVM, debug info, SQLite, optimization level, and version strings.

## Control Flow
The file computes defaults, probes Python, disables Python under selected sanitizers, maps built-in extension availability to default external extension options, forces Windows static defaults, declares all cache options, then applies derived relationships: diagnostics enables debug info/ref tracking/error log, unit-test asserts require unit tests, Windows chooses CRT mode, optimization flags replace prior `-O`/`/O` flags, GNU gets `-fno-strict-aliasing`, and Antithesis adds sanitizer coverage instrumentation.

## State And Persistence Behavior
It mutates CMake cache variables such as `ENABLE_SHARED`, `HAVE_DIAGNOSTIC`, `WT_ARCH`, `WT_OS`, `CC_OPTIMIZE_LEVEL`, `WT_OPTIMIZE_FLAGS_SAVED`, and `WT_DEBUG_FLAGS_INITIALIZED`. These values persist in a build directory and flow into generated headers and target flags.

## Dependencies And Integration Points
It includes `cmake/helpers.cmake` and `cmake/configs/version.cmake`, consumes library discovery variables such as `HAVE_LIBLZ4`, and relies on compiler identity variables established by `modes.cmake`. It feeds `wiredtiger_config.h.in`, library target definitions, extension builds, tests, and install metadata.

## Risks
Cache persistence is a major risk: once initialized, debug/optimization flags are guarded by internal variables and may not update unless cache variables change as expected. Dependency errors intentionally fail hard for explicit extension requests. Platform defaults can surprise cross-builds if `WT_OS`/`WT_ARCH` are not set before this file.

## Test Signals
Configure Debug, Release, sanitizer, Windows, and POSIX builds; toggle each extension with and without required libraries; verify generated `wiredtiger_config.h`, compile flags, and cache variables. Reconfigure after changing `CC_OPTIMIZE_LEVEL` to ensure replacement logic works.
