## sources/test-tools/syzkaller/pkg/kfuzztest-manager/manager.go

Purpose: standalone manager loop for fuzzing discovered KFuzzTest targets with syzkaller’s fuzzer engine and local KFuzzTest executor.

Important APIs/types/functions: `kFuzzTestManager`, `Config`, `NewKFuzzTestManager`, `Run`, `writePCs`, and `displayLoop`.

Control flow: resolves Linux/AMD64 target, extracts and activates KFuzzTest calls from vmlinux, filters enabled targets, logs enabled set, constructs a corpus and fuzzer with coverage enabled and no fault/collide/comparisons, then repeatedly obtains queue requests and submits them to the local executor until context cancellation. On exit it shuts down executor, stops display loop, and writes covered PCs to `pcs.out`.

State and persistence: stores fuzzer pointer, queue source, target, config; writes `pcs.out` in current working directory.

Dependencies and integration: integrates `kfuzztest`, `kfuzztest-executor`, fuzzer queue/corpus/stat packages, manager default exec opts, and Linux/AMD64 target assumptions.

Risks: busy loop if `source.Next()` returns nil. Target extraction is cached globally by kfuzztest and assumes one vmlinux per process. Output file path is fixed. Only Linux/AMD64 is supported despite KFuzzTest’s broader intent.

Test signals: no direct tests here; description-generation tests validate the extraction/build side.
