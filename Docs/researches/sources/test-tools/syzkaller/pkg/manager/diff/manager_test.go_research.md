# sources/test-tools/syzkaller/pkg/manager/diff/manager_test.go

Purpose: Validates the diff-fuzzer state machine under mocked kernels, repro callbacks, and base-verification runners.

Important tests: `TestNeedReproForTitle` verifies title filters for no output, SYZ failures, lost connection, stalls, and real kernel warnings/KASAN bugs. `TestDiffBaseCrashInterception` checks base crashes are surfaced on `BaseCrashes`. `TestDiffExternalIgnore` ensures ignored patched crashes are not reproduced. `TestDiffSuccess` checks patched crash -> repro -> base no-crash -> `PatchedOnly`. `TestDiffFailNoRepro` marks failed repro attempts completed. `TestDiffFailBaseCrash` reports base-affected repros instead of patched-only. `TestDiffFailBaseCrashEarly` avoids repro when base already saw the title. `TestDiffRetryRepro` checks retries until `maxReproAttempts`, then ignored.

Control flow and state: Tests finish corpus triage by setting mock progress to 1.0, start the diff loop, inject crash reports into channels, and assert store statuses or emitted channels. Repro callbacks and runner callbacks simulate success, failure, and base crash.

Dependencies and integration: Uses the harness from `diff_test.go`, `manager.DiffBugStatus*`, `report.Report`, and `repro.Result`. These tests pin the contract between `diffContext`, `DiffFuzzerStore`, and `ReproLoop`.

Risks: The tests focus on control-flow decisions, not real kernel execution, coverage filters, HTTP output, or filesystem artifact content. The retry test depends on timing and buffered channels but has a generous timeout.

Test signals: Strong coverage of high-risk duplicate/ignore/retry paths that prevent wasting VM time and prevent reporting bugs that also affect the base kernel.
