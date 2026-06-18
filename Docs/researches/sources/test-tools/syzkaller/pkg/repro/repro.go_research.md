# sources/test-tools/syzkaller/pkg/repro/repro.go

## Purpose

`repro.go` is syzkaller's crash reproducer extraction engine. Given a crash log, manager config, reporter, feature set, and VM pool, it finds a syz program that reproduces the crash, minimizes it, optionally converts it into a C reproducer, simplifies options, and validates reliability.

## Important APIs, Types, And Functions

Public types are `Result`, `Stats`, `Environment`, and `ErrEmptyCrashLog`; public entry points are `Run`, `Stats.FullLog`, and `Result.CProgram`. `Result` records the final `prog.Prog`, duration, `csource.Options`, C-repro status, final report, and reliability. `reproContext` holds crash identity, parsed log entries, timeouts, options, observed report titles, and executor abstraction. `execInterface` lets production code use `poolWrapper` while tests inject fake runners.

## Control Flow

`Run` delegates to `runInner`, which parses log entries, extracts the initial crash report, chooses timeout tiers based on crash type, creates starting C options from enabled features, and calls `reproContext.run`. `repro` trims entries after the crash, tries single-program extraction from the crash executor or last program per proc, then whole-log bisection and concatenation. After extraction it minimizes calls/arguments, tries C reproduction, simplifies syz and C options, and runs `calculateReliability` with up to ten validation attempts requiring at least 15 percent reliability.

Minimization uses `prog.Minimize`; multi-program bisection uses `minimize.SliceWithFixed` and preserves the crash-reported executor ID. Test execution funnels through `testProgs`/`testProg`/`testCProg` into `getVerdict`, which retries transient VM errors, filters suppressed reports, rejects non-leak reports for leak reproduction, and avoids low-priority crash diversion once a high-priority title is known.

## State, Dependencies, Integration, And Risks

State is in-memory except for VM-side execution and generated C source formatting. The package depends on `prog`, `csource`, `instance`, `mgrconfig`, `report`, `crash`, `targets`, VM dispatcher, and the bisection minimizer. Integration points include manager crash handling, dashboard artifacts, strace, VM execution, and syz-execprog/C executor paths. Risks are expensive VM loops, flaky crashes passing or failing reliability heuristics, lost original crash identity when unrelated high-priority crashes appear, races around no-output/lost-connection timeouts, and option simplification accidentally masking required setup. `checkOpts` specifically guards long non-repeating repros from false no-output bugs.

## Test Signals

`repro_test.go` covers bisection, option simplification validity, plain repro extraction, transient VM retry, too many errors, concatenation under `prog.MaxCalls`, flaky crash rejection, broken compiler C-repro skip, and avoiding low-priority lost-connection diversion. Benchmarks characterize reliability sampling cost.
