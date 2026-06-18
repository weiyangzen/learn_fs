# sources/test-tools/syzkaller/pkg/rpcserver/rpcserver.go

## Purpose

`rpcserver.go` manages FlatRPC connections from syz-executor runners, performs machine checks, distributes fuzzing requests, tracks runner lifecycle, and exposes server operations used by managers and local tests.

## Important APIs, Types, And Functions

`Config`, `RemoteConfig`, `Manager`, `Server`, `Stats`, `NewStats`, `NewNamedStats`, and `New` define the public surface. The private `server` owns the FlatRPC listener, target/timeouts, `vminfo.Checker`, queue distributor, runner map, feature state, coverage canonicalizer/filter, handshake channel, stats, and triaged-corpus flag. Lifecycle methods include `Listen`, `Serve`, `Close`, `Port`, `CreateInstance`, `StopFuzzing`, `ShutdownInstance`, `DistributeSignalDelta`, and `TriagedCorpus`.

## Control Flow

`New` translates manager config into RPC config, feature flags, sandbox flags, PC base, cover-edge/filter policy, and stats. `Serve` runs the listener and the first machine check under an `errgroup`. `handleConn` sends an auth cookie challenge, validates `ConnectRequest`, checks revisions unless VM-less, finds the pre-created runner, and hands off to `handleRunnerConn`. That method builds handshake options, obtains bug frames and machine-check files, runs `Runner.Handshake`, optionally sends corpus-triaged, and enters `connectionLoop`. `runCheck` uses `vminfo.Checker` output to compute enabled calls/features, prints diagnostics, asks the manager for the post-check queue source, swaps the dynamic source, and marks setup complete.

## State, Dependencies, Integration, And Risks

Persistent runtime state includes runner map under `mu`, atomic check/triage flags, coverage filter/modules, dynamic queue source, and stat counters. Dependencies include `flatrpc`, `queue`, `cover`, `backend`, `vminfo`, `mgrconfig`, `stat`, `signal`, `prog`, and VM dispatcher types. Integration points are manager startup, fuzzer corpus distribution, executor runner protocol, machine-check feature detection, coverage canonicalization, and crash report context. Risks include fatal revision mismatches, machine-check failure loops, unauthenticated-but-cookie-gated TCP clients, async runner sends after disconnect, races avoided by mutex/atomics, and signal filtering being disabled for non-Linux targets.

## Test Signals

`rpcserver_test.go` validates config feature derivation, revision checking, unknown VM connection rejection, and machine-check crash/restart handling through `LocalConfig`. Broader coverage comes from `runtest` local executor tests.
