# sources/test-tools/syzkaller/pkg/csource/csource_test.go

This file tests generated C source across syzkaller targets, option sets, pseudo syscalls, comments, sandbox signatures, and the LLM-oriented output path.

Important test helpers are `TestGenerate`, `testTarget`, `testPseudoSyscalls`, `testOne`, `TestExecutorMacros`, `TestSource`, `TestGenerateSandboxFunctionSignature`, and `TestWriteLLM`. `TestGenerate` iterates all targets whose compiler can run on the host, builds representative programs, and compiles generated C. `testTarget` varies option breadth by short/full mode and injects call properties such as fault injection, async, and rerun. `testOne` limits noisy failures, calls `Write`, checks include guard removal, then builds the result.

State is test-local plus a package-level `failedTests` counter used to cap failure spew. Dependencies include target descriptions, executor common headers, testutil race detection, generated programs, `Build`, and testify assertions. Integration points are broad: failures here indicate regressions in csource generation, target metadata, compiler flags, executor macros, or formatting assumptions.

Risk areas include high memory and compile cost, race-detector timeouts, host compiler availability, target-specific broken compilers, and generated output changes requiring expected snippet updates. The test signal is strong because it exercises both semantic generation and actual compilation. `TestWriteLLM` specifically verifies comments are present, sandbox scaffolding is omitted, syscalls appear inside `main`, and generated source builds.
