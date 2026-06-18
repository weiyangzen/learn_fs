# sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.h

Purpose: public interface for WiredTiger fuzz target helpers. It centralizes the global connection/session state and the sliced-input abstraction used when one fuzz byte string needs to represent multiple logical inputs.

Important APIs and types: `FUZZ_GLOBAL_STATE` stores `WT_CONNECTION *conn` and `WT_SESSION *session`; `extern FUZZ_GLOBAL_STATE fuzz_state` exposes the process-global instance. `fuzzutil_setup` initializes the connection/session lazily. `FUZZ_SLICED_INPUT` stores `const uint8_t **slices`, `size_t *sizes`, and `num_slices`. `fuzzutil_sliced_input_init/free` manage those arrays, and `fuzzutil_slice_to_cstring` converts a slice into an allocated C string.

Control flow and state: the header exposes ownership conventions but not cleanup for the global WiredTiger handles. Callers own strings returned by `fuzzutil_slice_to_cstring` and must call `fuzzutil_sliced_input_free` after successful sliced input initialization.

Dependencies and integration: includes `test_util.h`, which supplies WiredTiger types, test assertions/checking helpers, and standard support used by implementation files. It is included by `fuzz_util.c`, `modify/fuzz_modify.c`, and other fuzz targets.

Risks and test signals: because the API returns raw pointers and heap memory, callers must free per-invocation strings and sliced arrays. The `/* ![fuzzutil sliced input api] */` markers suggest documentation extraction or code snippet tests may rely on this block remaining stable. Coverage is through fuzz target build and execution under the fuzz CMake configuration.
