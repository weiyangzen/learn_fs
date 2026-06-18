# sources/storage-engines/wiredtiger/bench/workgen/workgen_int.h

## Purpose
`workgen_int.h` declares private runtime structures for workgen. It separates SWIG-visible API declarations from implementation-only execution state such as thread runners, monitors, operation internals, dynamic table runtime, throttling, and timestamp helpers.

## Important APIs, Types, and Functions
Important types include `tint_t`, `WorkgenTimeStamp`, `WorkgenException`, `Throttle`, `ThreadRunner`, `Monitor`, `TableRuntime`, `ContextInternal`, `OperationInternal` and subclasses, `TableInternal`, and `WorkloadRunner`. `ThreadRunner` owns per-thread session/cursor/RNG/buffer/stat state. `WorkloadRunner` owns the run-level thread vector, report stream, WT home path, start time, and stop flag.

## Control Flow
`WorkloadRunner` coordinates setup and execution. `ThreadRunner` methods prepare operations, generate keys/values, run operations, and maintain stats. `OperationInternal` subclasses parse operation config and implement non-table operations. `Monitor` periodically formats sampled stats. `Throttle` sleeps to enforce per-thread operation rates. `WorkgenTimeStamp` generates monotonic microsecond timestamps and sleeps fractional seconds.

## State and Persistence Behavior
Most state is runtime-only. `ContextInternal` maps URI strings to table IDs for static and dynamic tables, stores max record numbers, dynamic table in-use/delete flags, and mutexes. `TableRuntime` records mirror relationships that correspond to persisted table metadata created by `workgen.cpp`.

## Dependencies and Integration Points
The header depends on pthread-compatible types through implementation includes, WiredTiger C wrappers from `workgen_func.h`, time helpers from `workgen_time.h`, STL containers, and C math/unistd. It is the private contract between `workgen.cpp`, `workgen.h`, and C wrapper functions.

## Risks and Edge Cases
The private API exposes many raw pointers and manual ownership rules. `WorkgenTimeStamp::get_timestamp` is thread-local monotonic, so timestamps are monotonic per thread, not globally unless protected by external mutex use. `ContextInternal` has explicit single-context assumptions. Dynamic-table structures require correct shared-mutex discipline and atomic counter updates.

## Test Signals
Coverage should come through workgen runtime tests: multi-thread workloads, throttled workloads, timestamped transactions, dynamic table create/drop, mirrored table operations, and monitor sampling. Static analysis is useful for raw pointer ownership and lock discipline.
