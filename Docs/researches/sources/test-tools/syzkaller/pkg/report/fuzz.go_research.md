# Research: sources/test-tools/syzkaller/pkg/report/fuzz.go

Purpose: provides a package-level fuzz entry point that stress-tests every non-stub reporter implementation against arbitrary byte slices. It asserts core reporter invariants rather than validating one OS-specific title.

Important APIs/types/functions: `Fuzz(data []byte) int` is the exported fuzz target. `fuzzReporters` is an initialized map from OS name to `*Reporter`, built by iterating `ctors`, skipping Windows/stubs and unsupported AMD64 targets, and calling `NewReporter` with minimal `mgrconfig.Config`.

Control flow: for each reporter, the fuzzer checks that `ContainsCrash(data)` agrees with `Parse(data) != nil`. If a report is found, it calls `Symbolize`, verifies non-empty title/report/output, validates start/end/skip position relationships for all OSes except Fuchsia, and reparses from `StartPos` to ensure stable discovery of the same report. Any invariant failure panics so go-fuzz/native fuzzing can minimize the input.

State and persistence: reporter instances are package-level cached test objects with no persistent storage. The only mutable state is per-report symbolization state; the fuzzer intentionally calls `Symbolize` once per parsed report to exercise that guard.

Dependencies and integration points: depends on `mgrconfig`, `targets`, the global `ctors` table in `report.go`, and every concrete reporter. It is an integration-level harness for parser consistency across Linux, BSDs, Darwin, Fuchsia, gVisor, and common syzkaller runtime errors.

Risks: because `fuzzReporters` is initialized at package load time, constructor panics or target-definition changes can break all fuzzing. Minimal configs mean symbolization paths are usually absent, so full addr2line paths are not fuzzed. Fuchsia is exempted from position checks because its parse-time symbolization currently makes positions imperfect, so regressions there need fixture tests.

Test signals: `TestFuzz` in `report_test.go` seeds historically problematic inputs, including malformed Linux prefixes, truncated Zircon panics, BSD vnode panics, and boot messages. Fuzz failures are high-value because they expose parser panics, crash-detection disagreement, empty reports, or invalid offsets.
