# sources/storage-engines/wiredtiger/tools/voidstar/include/instrumentation.h

Purpose: declares the Antithesis instrumentation interface used by instrumented programs or harnesses to request fuzzer input, emit messages/guidance, and report coverage.

Important APIs and control flow: input functions include `fuzz_getchar()`, `fuzz_get_random()`, `fuzz_coin_flip()`, and `fuzz_getblob()`. Output functions include `fuzz_set_source_name()`, info/error message and data calls, `fuzz_png()`, `fuzz_bytes()`, `fuzz_kv32_pairs()`, `fuzz_flush()`, and `fuzz_exit()`. Coverage callbacks include LLVM sanitizer coverage hooks `__sanitizer_cov_trace_pc_guard_init()` and `__sanitizer_cov_trace_pc_guard()`, plus manual module/edge APIs `init_coverage_module()` and `notify_coverage()`. Comments describe three implementations: stub `libvoidstar.so`, legacy socket-based instrumentation, and deterministic hypervisor instrumentation.

State and persistence behavior: this header declares interfaces only. Implementations may buffer output, set a process/source name, send stateful coverage messages, terminate the process, or synchronize with a fuzzer/hypervisor.

Dependencies and integration points: C/C++ compatible via `extern "C"`, includes `stddef.h`, `stdint.h`, and `stdbool.h`. WiredTiger or tests link against the stub library and can substitute real instrumentation with `LD_PRELOAD` or environment setup.

Risks: comments document significant runtime semantics: output buffering can cross timing boundaries across multiple library copies, deterministic hypervisor calls are not usable outside the hypervisor, and coverage volume can be expensive. The reserved LLVM sanitizer symbol names require diagnostic suppression for Clang.

Test signals: compile/link tests against `libvoidstar.so` validate ABI availability. Runtime Antithesis campaigns validate input/output/coverage behavior under the chosen implementation.
