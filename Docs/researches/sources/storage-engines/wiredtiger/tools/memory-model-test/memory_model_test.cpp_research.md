# sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp -->
## sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp

### Purpose
`memory_model_test.cpp` is a standalone memory-ordering litmus-test driver. It repeatedly runs pairs of operations in two threads to observe whether out-of-order effects occur with plain writes/reads, compiler barriers, CPU memory barriers, and GCC/Clang atomic builtins.

### Important APIs, Types, and Functions
`thread_function` waits on a start semaphore, adds a random delay, runs a supplied lambda, and releases an end semaphore for each iteration. `test_config` packages a test name, description, two thread lambdas, an out-of-order predicate, and whether out-of-order results are allowed. `perform_test` runs a configured pair, resets shared variables per iteration, coordinates workers, counts predicate hits, reports totals, and flags forbidden reorderings. `thread_pair` declares padded shared variables, builds lambdas for write/read and two-write/two-read cases, defines test configurations, and runs them. `main` parses `-n` loop count and `-p` number of thread pairs.

### Control Flow
At startup the program chooses `std::binary_semaphore` or `basic_semaphore`, chooses an architecture barrier instruction (`mfence` on x86_64, `dmb ish` on aarch64), prints environment details, and starts the requested number of thread-pair drivers. Each test spawns two worker threads once and drives them through `loop_count` iterations via semaphores.

### State and Persistence
State is volatile runtime state only: padded integers `x`, `y`, `r1`, `r2`, semaphores, random generators, and counters. Output is printed to stdout; no files are written.

### Dependencies and Integration Points
Depends on C++ threads, semaphores or the fallback semaphore, inline assembly barriers, `unistd.h` getopt, and compiler atomic builtins. It is built by the local CMake file and used as a diagnostic/development tool rather than WiredTiger runtime code.

### Risks and Test Signals
The shared variables are plain `int` and intentionally data-racy for litmus purposes; sanitizers will report races. The `"one barrier and one atomic"` test description does not match the code, which uses atomics in both lambdas. No barrier definition exists for non-x86_64/non-aarch64 architectures. `atoi` permits zero/negative loop or pair counts without validation, and percentage calculations divide by `iterations` after the loop. Test signals include small smoke runs, architecture-specific expected forbidden-count behavior, and build with/without `AVOID_CPP20_SEMAPHORE`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/memory_model_test.cpp -->
