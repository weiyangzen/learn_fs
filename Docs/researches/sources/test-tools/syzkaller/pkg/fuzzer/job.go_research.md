# sources/test-tools/syzkaller/pkg/fuzzer/job.go

## Purpose
This file implements asynchronous fuzzer jobs: triage, minimization, corpus insertion, smash mutation, fault injection, and comparison-guided hints. It is where potentially interesting execution results are deflaked, minimized, and turned into persistent corpus inputs and follow-up work.

## Important APIs, Types, And Functions
`JobType` identifies `triage`, `candidate_triage`, `smash`, and `hints`. `JobInfo` provides introspection fields and a synchronized log buffer. `genProgRequest` and `mutateProgRequest` build execution requests for generated and mutated programs. `triageJob` stores the program, executor to avoid, flags, queue, candidate calls, and job info. `triageCall` tracks original errno, new signal, deflake run signals, stable signal, new stable signal, cover, and raw cover.

`triageJob.run` logs input and calls, deflakes, then handles each call concurrently. `deflake` reruns the program with signal/cover collection, avoids already-used executors, merges flaky max signal, computes signal common to required runs, and records coverage/raw cover. `stopDeflake` encodes different stopping policies for snapshot mode, new fuzz programs, and corpus retriage. `minimize` wraps `prog.Minimize` and reexecutes candidates to preserve new stable signal. `handleCall` starts smash, hints, and fault-injection jobs as configured and saves a new corpus input. `smashJob`, `faultInjectionJob`, and `hintsJob` implement follow-up execution strategies.

## Control Flow
Triage begins after `processResult` finds new signal. It reruns the same program until enough stable signal is found or stopping conditions say more runs are not useful. Calls with new stable signal are minimized unless already minimized, filtered by call name, saved to the corpus, and used to schedule extra work. Smash runs 25 mutations. Fault injection walks `FailNth` from 1 to 100 until the executor stops injecting. Hints first collect stable comparisons over three runs, applies the hints limiter, then mutates with hints and executes each generated program.

## State And Persistence Behavior
Persistent output is delegated to `Config.Corpus.Save` with program, call, stable signal, serialized cover, and optional raw cover. Job logs and exec counters are held in `JobInfo` for live introspection. Deflake state is per job/call and includes arrays of signal intersections by run count. Fault injection modifies cloned programs only.

## Dependencies And Integration Points
The code depends on `prog` generation/mutation/minimization/hints APIs, `pkg/corpus`, `pkg/cover`, `pkg/signal`, `flatrpc` call flags and exec flags, and the queue executor interface. It is launched by `Fuzzer.startJob` and observed via `Fuzzer.RunningJobs`.

## Risks
Deflake thresholds are probabilistic and tuned for flaky reproduction; changes can create duplicate work or drop useful inputs. `handleCall` launches follow-up jobs before corpus save completion is externally visible. Concurrent per-call handling shares the same base job and fuzzer state, relying on downstream thread safety. Hints can generate many executions and are limited only by `hintsLimiter` and mutation behavior.

## Test Signals
`job_test.go` targets deflake signal/coverage behavior. `fuzzer_test.go` indirectly exercises triage, corpus insertion, and follow-up jobs in an executor-backed fuzz run.
