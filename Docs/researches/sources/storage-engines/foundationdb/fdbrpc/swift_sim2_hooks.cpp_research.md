# sources/storage-engines/foundationdb/fdbrpc/swift_sim2_hooks.cpp

## Purpose
`swift_sim2_hooks.cpp` bridges Swift concurrency into the FoundationDB simulator. It implements the Swift global enqueue hook for Sim2 so Swift jobs scheduled while running in simulation are inserted into the simulator task queue instead of being executed by the normal Swift runtime executor path.

## Important APIs, Types, And Functions
The sole exported implementation is `sim2_enqueueGlobal_hook_impl(swift::Job*, void (*)(swift::Job*) swiftcall)`, declared with `SWIFT_CC(swift)`. It obtains `g_simulator`, asserts it exists, and calls `ISimulator::_swiftEnqueue(job)`. The second function-pointer parameter is intentionally unused because Sim2 provides the enqueue behavior.

## Control Flow
Swift runtime code calls this hook when a Swift job is globally enqueued under the configured concurrency hooks. The hook synchronously forwards the job to the simulator. In `sim2.cpp`, `_swiftEnqueue` maps the Swift job priority to a Flow `TaskPriority`, captures the current simulated process, wraps the job in a `PromiseTask`, and places it in `taskQueue`. The job is later executed by the simulation run loop under the captured process context.

## State And Persistence Behavior
This file owns no state. It depends on global simulator state and requires `g_simulator` to be initialized. All durable behavior is delegated to the simulator queue and Swift job execution.

## Dependencies And Integration Points
It includes simulator, Flow, network, TLS, Swift concurrency hooks, and Swift ABI task headers. It is only meaningful in Swift-enabled builds where FoundationDB's Swift interoperability hooks are active. Its correctness depends on `Sim2::_swiftEnqueue` preserving process context and priority mapping.

## Risks And Test Signals
Calling the hook before simulator startup aborts on `ASSERT(sim)`. If the Swift runtime changes the hook ABI or job ownership semantics, this bridge can break at integration time. The hook ignores the original enqueue function, so fallback behavior is unavailable in simulation. Swift-enabled simulation tests should show Swift tasks executing deterministically on the expected simulated process; build/link failures around Swift ABI headers or unresolved hook symbols are the primary static signals.
