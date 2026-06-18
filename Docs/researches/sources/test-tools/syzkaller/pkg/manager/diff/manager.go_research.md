# sources/test-tools/syzkaller/pkg/manager/diff/manager.go

Purpose: Orchestrates differential patch fuzzing across base and patched kernels. It loads seeds, runs both kernel contexts, feeds patched programs into the base queue, schedules reproductions, verifies whether reproducers crash the base kernel, and reports patched-only bugs.

Important APIs and types: `Config` contains channels (`PatchedOnly`, `BaseCrashes`), store, artifact directory, triage and patched-coverage deadlines, external `IgnoreCrash`, and injectable `runner`/`runRepro`. `Bug` carries a patched report and repro. `Run` is the package entry point. `Kernel` abstracts concrete kernel contexts. `diffContext` owns runtime state and implements `manager.ReproManagerView` through `NeedRepro`, `RunRepro`, and `ResizeReproPool`.

Control flow: `Run` sets up base/new kernels, loads immutable seeds for the patched kernel, creates a random queue so patched-generated programs can be duplicated to the base source, initializes repro callbacks, optionally creates an HTTP server, then runs `diffContext.Loop`. The loop starts the HTTP server, delayed repro loop after 90% triage or timeout, patched-coverage monitor after 99% triage, and both kernel loops. It handles base crashes, patched crashes, repro completion on patched, and base-verification runner results.

State and persistence: `DiffFuzzerStore` receives `PatchedCrashed`, `BaseCrashed`, `BaseNotCrashed`, `UpdateStatus`, and `SaveRepro` calls. `reproAttempts` is mutex-protected and caps attempts per title. Status moves through pending/verifying/completed/ignored. Patched-only bugs are emitted only after a reliable patched repro does not crash base.

Dependencies and integration: Uses manager repro loop, report/repro packages, flatrpc features, VM dispatcher capacity, stats logging, seed loading, HTTP dashboard, and optional external ignore service.

Risks: False positives are mitigated but still depend on repro reliability and base runner behavior. External `IgnoreCrash` failures are logged and treated as non-ignore. `NeedRepro` uses a background timeout rather than caller context. A typo in a log message is harmless but visible. Patched-coverage monitoring assumes focus areas were prepared.

Test signals: `manager_test.go` covers base-crash interception, external ignore, successful patched-only flow, failed repro, base crash after repro, early base crash dedupe, and retry cap behavior.
