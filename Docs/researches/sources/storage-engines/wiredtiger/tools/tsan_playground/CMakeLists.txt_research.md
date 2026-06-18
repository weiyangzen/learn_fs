# sources/storage-engines/wiredtiger/tools/tsan_playground/CMakeLists.txt

Purpose: declares a build matrix of TSAN playground executables, each compiling the same `tsan_playground.c` with a different atomic/barrier API implementation macro.

Important APIs and control flow: sets C standard to C11, then calls `create_test_executable()` for C11 atomics, C11 acq/rel barriers, C11 full barriers, GCC atomics, GCC acq/rel barriers, GCC full barriers, WT atomics, WT acq/rel barriers, WT store/load-with-barriers, WT full barriers, and dummy atomics. GCC barrier variants add `-Wno-error=tsan` because TSAN warns about unsupported `atomic_thread_fence`.

State and persistence behavior: build-system only; it produces executables under the build tree.

Dependencies and integration points: depends on the repository's CMake `create_test_executable` helper and the header variants in the same directory. The executables are consumed by `collect_warnings.sh`.

Risks: targets using WT headers require include paths and generated headers supplied by the broader WiredTiger build. The matrix can compile but still have different TSAN runtime behavior, so build success is not enough.

Test signals: successful CMake configuration/build creates `tools/tsan_playground/tsan_playground_*` executables. Runtime signal comes from `collect_warnings.sh`.
