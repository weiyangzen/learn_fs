# sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.c

Purpose: shared libFuzzer support for WiredTiger fuzz targets. It owns the process-global `FUZZ_GLOBAL_STATE fuzz_state`, lazily opens a small WiredTiger home, and provides helpers for splitting byte input into multiple logical arguments.

Important APIs and functions: `fuzzutil_setup` creates a per-process home named `WT_TEST_<pid>`, recreates it, calls `wiredtiger_open` with create/cache/statistics settings, and opens one session. `fuzzutil_sliced_input_init` searches the input for a caller-provided separator using `memmem`, stores pointers and lengths into heap arrays, and succeeds only when exactly `req_slices` are present. `fuzzutil_sliced_input_free` releases those arrays. `fuzzutil_slice_to_cstring` copies a byte slice into a NUL-terminated string.

Control flow and state: the first fuzz invocation initializes `fuzz_state`; later invocations reuse the same connection/session. Sliced input is zero-copy with respect to the fuzzer buffer; only the slice pointer/length arrays are allocated. On parse failure the helper frees partial arrays and returns `false`.

Dependencies and integration: depends on `fuzz_util.h`, `test_util.h`, WiredTiger public API, and GNU `memmem`. It is built as the shared `fuzz_util` library and consumed by fuzz targets such as config and modify fuzzers.

Risks and test signals: no teardown exists for `fuzz_state`, which is acceptable for fuzzer process lifetime but leaks by design. Invalid separator counts reject many early corpus inputs. `fuzzutil_sliced_input_init` assumes nonzero separator size and does not pre-count separators, so malformed input still allocates briefly. Test signal is libFuzzer exercising targets without worker home collisions.
