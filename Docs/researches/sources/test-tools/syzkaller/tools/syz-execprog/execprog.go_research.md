# sources/test-tools/syzkaller/tools/syz-execprog/execprog.go

Purpose: `syz-execprog` executes syzkaller programs or corpus databases locally through the executor/RPC stack, optionally collecting coverage, hints, output, glob expansion results, or running as a simple stress fuzzer.

Important APIs and flow: `main` parses target/executor/sandbox/feature/repeat/procs/coverage/stress/glob flags, resolves `prog.Target`, converts csource feature flags to FlatRPC feature masks, parses stress syscall filters, builds executor environment and exec flags, loads programs from DB or logs, creates a `Context`, and runs `rpcserver.RunLocal` with a `LocalConfig`. `Context.machineChecked` receives feature/syscall data, sets stress choice tables, and returns queue options. `Next` generates glob requests, random/mutated stress programs, or sequenced corpus programs. `Done` prints call results, hints, and coverage, increments atomics, and cancels when repeat count is satisfied. Coverage is dumped per program/call with PCs normalized through `backend.PreviousInstructionPC`.

State and persistence: state includes loaded programs, random source, queue position, result counters, and optional coverage files named from `-coverfile`. It reads corpus DBs/logs and executor binary path. Stress mode is long-running when repeat is 0.

Dependencies and integration: integrates `pkg/rpcserver`, `pkg/fuzzer/queue`, `flatrpc`, executor binary, target descriptions, `pkg/db`, `prog`, coverage backend, csource features, and VM info. It is a key standalone executor harness used by reproducer and debugging workflows.

Risks: unsupported or mismatched executor/target features can fail at runtime. `loadPrograms` silently skips DB records that fail deserialization but fatals on unreadable files. Coverage dumping creates many files. Stress mode without syscall filtering can generate broad workloads. The deprecated `-collide` flag is accepted but ignored for compatibility.

Test signals: no direct test in this subset. Indirect coverage comes from executor, RPC server, queue, DB, and target parser tests plus real syzkaller reproducer workflows.
