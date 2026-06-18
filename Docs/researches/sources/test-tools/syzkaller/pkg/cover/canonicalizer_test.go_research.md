# sources/test-tools/syzkaller/pkg/cover/canonicalizer_test.go

Purpose: exercises canonical and reverse coverage PC conversion across fuzzer instances with different module layouts.

Important APIs/types/functions: local test harness types `RPCServer`, `Fuzzer`, `canonicalizeValue`, helpers `runTest`, `connect`, and `initModules`; tests `TestNilModules`, `TestDisabledSignals`, `TestModules`, and `TestChangingModules`.

Control flow: the fake RPC server initializes the first fuzzer's module list as canonical, then connects additional fuzzers. Tests populate coverage/signature/bitmap arrays, run either canonicalization or decanonicalization, and compare with expected arrays using `reflect.DeepEqual`.

State and persistence: all fake server/fuzzer state is in memory.

Dependencies and integration: imports `vminfo.KernelModule` to mirror real module metadata. It targets public `NewCanonicalizer` and instance conversion methods.

Risks: harness models only simple numeric module names and address ranges. It does not test overlapping modules, zero-size modules, or logging of discarded PCs.

Test signals: strong regression coverage for the intended multi-fuzzer module-address use case, including disabled signal mode and discarding coverage from modules absent in the canonical build.
