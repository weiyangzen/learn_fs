# sources/sync-backup/git-lfs/t/git-lfs-test-server-api/main.go

## Purpose
Command-line compliance probe for a Git LFS batch API server. It builds or reads known existing and missing object IDs, pins Git LFS transfer machinery to a supplied endpoint, and runs registered upload/download tests against that endpoint.

## Important APIs, Types, and Control Flow
Key types are `TestObject` (`Oid`, `Size`) and `ServerTest` (`Name`, callback). `RootCmd` exposes `--url`, `--clone`, and `--save`. `testServerApi` validates arguments, creates a temporary test repo through `t.NewRepo`, builds a manifest with `buildManifest`, either reads OID fixtures with `readTestOids` or creates them with `buildTestData`, optionally saves them, and calls `runTests`. `constantEndpoint` overrides endpoint discovery so all operations use the target endpoint. `callBatchApi`, `interleaveTestData`, and `uploadTransfer` are shared by upload/download test files.

## State, Persistence, and Dependencies
The tool creates local Git/LFS objects, uploads 50 existing objects when generating fresh test data, and may persist OID lists as `<prefix>_exists` and `<prefix>_missing`. It depends on Git LFS packages `lfsapi`, `lfshttp`, `tq`, `fs`, `tasklog`, and test utilities under `t/cmd/util`, plus Cobra.

## Integration Points, Risks, and Test Signals
The `init` in this file registers CLI flags; `init` functions in companion files register tests through `addTest`. Risks include ignored parse errors in `readTestOids`, deterministic but global `math/rand` seeding, and fatal process exits inside library-like helpers. Test signals are per-test OK/FAILED lines, final `All tests passed`, correct batch response lengths, and expected transfer links or error codes.
