# sources/storage-engines/wiredtiger/test/fuzz/config/fuzz_config.c

Purpose: libFuzzer target for WiredTiger configuration parser lookups.

Important APIs and functions: `LLVMFuzzerTestOneInput`, `fuzzutil_setup`, `fuzzutil_sliced_input_init`, `fuzzutil_slice_to_cstring`, `__wt_config_getones`, and `fuzzutil_sliced_input_free`.

Control flow: initializes fuzz utility state, splits input into exactly two slices separated by `|`, converts slice 0 to a null-terminated key and slice 1 to a null-terminated config string, calls `__wt_config_getones` with `fuzz_state.session`, ignores the result value, frees all temporary inputs, and returns 0. Inputs without two slices are ignored.

State and persistence: creates heap strings for fuzzer data and uses shared fuzz utility session state. It does not persist files directly.

Dependencies and integration: built by `test/fuzz/CMakeLists.txt` and run by `fuzz_run.sh`. It depends on `fuzz_util.h`, WiredTiger internal config parser APIs, and the fuzzer runtime entrypoint contract.

Risks and test signals: the delimiter split means fuzz coverage focuses on key/config combinations, not arbitrary binary config alone. Crashes, assertion failures, sanitizer reports, leaks, or timeouts are meaningful parser robustness signals.
