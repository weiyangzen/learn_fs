# sources/test-tools/syzkaller/pkg/fuzzer/queue/stats.go

## Purpose
This file declares shared queue/fuzzing stats that are updated and read by different parts of the system.

## Important APIs, Types, And Functions
`StatNoExecRequests` tracks stalls when the fuzzer has no execution requests. `StatNoExecDuration` tracks aggregate stall duration in nanoseconds per second. `StatExecBufferTooSmall` tracks program serialization overflow of the executor buffer.

## Control Flow
There are no functions. Stats are registered at package initialization through `stat.New`.

## State And Persistence Behavior
Stats are process-global metric values managed by the `stat` package. They are not persisted by this file.

## Dependencies And Integration Points
The only dependency is `pkg/stat`. Executor/RPC loops and serialization paths can update these counters to expose scheduling and buffer issues.

## Risks
Global stat registration makes names part of the monitoring interface; renaming affects dashboards or consumers.

## Test Signals
No direct tests in this item.
