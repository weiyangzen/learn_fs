# sources/storage-engines/wiredtiger/test/utility/test_util.h

## Purpose
`test_util.h` is the shared C test utility contract for WiredTiger tests. It centralizes constants, platform path definitions, configuration string macros, option/state structures, assertion/checking macros, inline timestamp/string helpers, and prototypes for filesystem, backup, LazyFS, operation-thread, tiered/disaggregated, random, modify, and process utilities.

## Important APIs and types
The key type is `TEST_OPTS`, which carries parsed command-line options, paths, random states, tiered/disaggregated settings, connection/session handles, shared thread flags, and resource pointers cleaned by `testutil_cleanup`. `TEST_PER_THREAD_OPTS` wraps per-worker operation counters. `WT_LAZY_FS`, `WT_FILE_COPY_OPTS`, and `WT_MKDIR_OPTS` describe LazyFS state and utility file operations. Macros include `testutil_assert`, `testutil_assert_errno`, `testutil_check`, `testutil_snprintf`, `testutil_drop`, `testutil_verify`, `WT_OP_CHECKPOINT_WAIT`, `testutil_system`, and the configuration templates used by `misc.c` and `tiered.c`.

## Control flow and behavior
The header enforces a fail-fast test style: checking macros call `testutil_die` with function and line context. Inline helpers `u64_to_string`, `u64_to_string_zf`, `testutil_timestamp_parse`, and `maximum_stable_ts` provide small utility logic without a separate compilation unit. `TESTUTIL_DISAGG_INIT` is intentionally exhaustive and documents that new disaggregated fields must be added to the initializer.

## State, dependencies, and integration
The header includes `wt_internal.h` and conditionally includes `windows_shim.h`, exposing test helpers to C and C++ via `extern "C"`. It binds many implementation files together: `misc.c`, `parse_opts.c`, `thread.c`, `tiered.c`, `util_modify.c`, `util_random.c`, backup helpers, LazyFS helpers, filesystem helpers, and Windows shims. `custom_die` and `progname` are declared as process-global integration points.

## Risks and test signals
Because this header exposes many macros and a large mutable `TEST_OPTS`, changes have high blast radius. Risks include macro double-evaluation if future macros are not careful, incomplete initialization when adding fields, config-buffer size assumptions, and platform divergence under `_WIN32`. Test signals are compile failures across C/C++ test targets, assertion output quality, successful Windows builds, tiered/disaggregated config strings, and command-line option behavior in tests using the shared parser.
