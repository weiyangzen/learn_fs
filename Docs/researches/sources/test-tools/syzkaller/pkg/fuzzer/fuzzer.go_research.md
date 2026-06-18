# sources/test-tools/syzkaller/pkg/fuzzer/fuzzer.go

## Purpose
This file defines the central `Fuzzer` object: configuration, execution queues, coverage tracking, candidate intake, request generation, execution result processing, choice-table maintenance, job tracking, and default executor options.

## Important APIs, Types, And Functions
`Fuzzer` embeds `Stats` and stores `Config`, `Cover`, context, RNG, target, hints limiter, running jobs, choice table state, and `execQueues`. `Config` controls corpus, logging, snapshot/coverage/comparison/collide/fault-injection modes, enabled calls, mutation exclusions, raw cover fetching, patch testing, and KFuzzTest mode. `NewFuzzer` initializes defaults, stats, cover, queue source ordering, choice table updater, and optional debug logging.

`execQueues` contains candidate, triage, and smash queues. `newExecQueues` orders sources as candidate triage, candidate execution, regular triage, alternated smash, then generated fuzz. `Next` returns the next request and panics on nil. `AddCandidates` enqueues corpus or hub candidates with signal collection and candidate flags. `execute`, `executeWithFlags`, `prepare`, and `enqueue` attach result callbacks and submit to a queue executor.

`processResult` handles completed requests. It triages newly discovered signal unless the program is already in triage or hanged, creates `triageJob`s, records execution time and overflow stats, retries corpus candidates for flaky coverage or risky crashes, and decrements candidate stats. `triageProgCall` computes signal priority, updates `Cover`, filters by `NewInputFilter`, and records `triageCall` state. `DefaultExecOpts` translates manager configuration and feature bits into `flatrpc.ExecOpts`.

## Control Flow
Normal fuzzing flows from `Next` through ordered queue sources. If queues are empty, `genFuzz` mutates a corpus program or generates a new program, optionally transforms it for collide mode, and attaches processing callbacks. On completion, `processResult` may start asynchronous triage jobs before unblocking waiters. Choice table refresh is signaled over a lossy channel when corpus growth crosses thresholds, and a goroutine rebuilds it.

## State And Persistence Behavior
Long-lived process state includes coverage max signal, corpus-driven choice table, stats, and running job registry. Persistent corpus state is delegated to `Config.Corpus.Save` in job code. Candidate retry state is stored in queue request flags and `attempt` recursion. Choice table update uses a mutex and only replaces the table when built from at least as many programs as the previous one.

## Dependencies And Integration Points
This code ties together `pkg/corpus`, `pkg/flatrpc`, `pkg/fuzzer/queue`, `pkg/signal`, `pkg/stat`, `prog`, `csource`, and `mgrconfig`. Queue requests use `flatrpc.ExecOpts`; results use `ProgInfo` and per-call `CallInfo`. The fuzzer is consumed by RPC/local executor loops that call `Next` and later `Done`.

## Risks
The nil panic in `Next` assumes `genFuzz` always succeeds; an empty or broken generation path would crash the fuzzer. Triage is intentionally skipped for hanged programs, which avoids executor starvation but can miss signal. Candidate retries differ in snapshot and non-snapshot mode, so crash attribution and flakiness handling are configuration-sensitive. `ctMu` is a normal mutex with a TODO for read/write locking, so choice-table access can serialize hot paths.

## Test Signals
`fuzzer_test.go` integration-runs a local executor in `TestFuzz`, benchmarks `Next`/`Done` loops, emulates execution signal, and checks goroutine cleanup. Job tests indirectly validate triage support logic.
