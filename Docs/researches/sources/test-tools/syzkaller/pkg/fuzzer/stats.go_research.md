# sources/test-tools/syzkaller/pkg/fuzzer/stats.go

## Purpose
This file defines the fuzzer's metric registry and per-syscall overflow counters.

## Important APIs, Types, And Functions
`Stats` contains per-syscall `SyscallStats` plus many `stat.Val` pointers for candidates, new inputs, running jobs by type, execution counts by source/type, execution time, and coverage/comparison overflows. `SyscallStats` stores atomic cover and comparison overflow counters. `newStats(target)` allocates one syscall stat per syscall plus one extra/remote bucket and registers all named metrics.

## Control Flow
`newStats` is a constructor returning a populated `Stats` value. Metrics use graph, stacked graph, rate, distribution, console, link, and no-graph options.

## State And Persistence Behavior
Stats are in-memory process metrics. Per-syscall overflow counters are atomics updated by `Fuzzer.handleCallInfo`. The extra slot handles aggregate extra/remote call info.

## Dependencies And Integration Points
It depends on `pkg/stat` and `prog.Target`. `Fuzzer` embeds `Stats`, jobs update job/execution stats, and queue/fuzzer web endpoints can link job stats by type.

## Risks
Metric names and graph groupings are external observability contracts. The `Syscalls` slice indexing assumes syscall IDs align with `target.Syscalls` and reserves the last slot for extra info.

## Test Signals
No direct tests in this item. Integration tests observe some stats indirectly through corpus/signal behavior and debug logging.
