# sources/storage-engines/wiredtiger/test/fuzz/fuzz_run.sh

Purpose: standard runner for WiredTiger libFuzzer binaries.

Important commands and variables: accepts `<fuzz-test-binary> [fuzz-test-args]`, removes previous `WT_TEST_*`, `.profraw`, and `fuzz-*.log` outputs, exports `LLVM_PROFILE_FILE=WT_TEST_%p.profraw`, and executes the fuzzer with `-jobs=8 -runs=100000000 -close_fd_mask=3`.

Control flow: validates an argument, stores and shifts the binary path so extra args pass through to the fuzzer, cleans prior run artifacts, sets coverage profile naming, then starts libFuzzer with parallel workers, a finite large run count, suppressed stdout/stderr, and any caller-provided corpus/options.

State and persistence: creates `WT_TEST_<pid>` homes, per-worker profiler files, libFuzzer logs, and crash artifacts in the current directory. It removes old matching artifacts before each run.

Dependencies and integration: used by CTest entries in `test/fuzz/CMakeLists.txt`. It assumes the target is a libFuzzer binary and benefits from ASan/coverage builds.

Risks and test signals: `-close_fd_mask=3` prevents log spam but hides target output during the run; reproducing crashes without the mask may be needed. Large run count can be expensive, and cleanup wildcards require a dedicated working directory.
