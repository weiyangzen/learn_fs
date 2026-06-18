# sources/storage-engines/foundationdb/documentation/tutorial/make_h2o.actor.cpp

## Purpose
Flow actor solution to the Building H2O concurrency exercise. It synchronizes two hydrogen actors with one oxygen actor per molecule.

## Important APIs, Types, and Functions
Globals `h_seqno`, `o_seqno`, `h_queue`, and `wakeup` track actor ids and promises. `hydrogen()` registers a promise and waits for an oxygen id. `oxygen()` waits on `AsyncTrigger`, consumes two hydrogens, and sends its id. `orchestrate()` creates and balances batches. `main()` initializes Flow and runs the orchestrator.

## Control Flow
The orchestrator randomly starts H/O actors until a threshold, adds actors to enforce a 2:1 ratio, triggers readiness, and waits for all batch actors. Oxygen actors drain queued hydrogens until two are bound; hydrogen actors return when their promise is fulfilled.

## State and Persistence Behavior
All state is process-local. `wakeup` holds raw pointers to actor-local promises until erased by oxygen actors. No external persistence exists.

## Dependencies and Integration Points
Uses Flow `Promise`, `Future`, `AsyncTrigger`, `waitForAll`, deterministic randomness, `fmt`, network initialization, and actor compiler support. Built as `make_h2o`.

## Risks
Global mutable state and raw promise pointers are safe only under the intended actor lifetimes. Missing final triggers or waits can deadlock. Large loop counts make failures noisy.

## Test Signals
Run with smaller batch sizes while debugging; assert no leftover `wakeup` entries and no H/O ratio assertion failures. Build ensures actor compiler compatibility.
