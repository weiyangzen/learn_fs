# sources/user-network-fs/s3fs-fuse/test/run_tests_using_sanitizers.sh

## Purpose
Runs the test suite under libstdc++ debug mode, multiple sanitizers, and Valgrind to expose memory, undefined behavior, thread, and container misuse issues.

## Important APIs, Types, And Control Flow
Uses strict bash options, sets debug-friendly `COMMON_FLAGS`, then cycles through clean/configure/build/check for `_GLIBCXX_DEBUG`, AddressSanitizer with leak/use-after-return options, ThreadSanitizer, UndefinedBehaviorSanitizer with extra conversion/bounds checks, and Valgrind with high retries and S3Proxy HTTP URL. MemorySanitizer is documented but disabled pending custom libc++.

## State And Persistence
Mutates build outputs repeatedly and runs integration tests that create mount, cache, and S3Proxy state. No source edits are made.

## Dependencies And Integration Points
Depends on GCC/libstdc++ debug mode, clang++, sanitizer runtimes, Valgrind, configure/make, and the test harness. Integrates as a heavyweight CI/local validation lane.

## Risks And Test Signals
Sanitizer availability is platform/toolchain-sensitive and ThreadSanitizer can be noisy with external libraries. Valgrind runs are slow and retry-heavy. Passing this script is a high-value signal for `ThreadPoolMan`, cache, and string/binary utilities.
