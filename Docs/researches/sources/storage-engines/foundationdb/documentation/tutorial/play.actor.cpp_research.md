# sources/storage-engines/foundationdb/documentation/tutorial/play.actor.cpp

## Purpose
Minimal Flow playground template for temporary experiments.

## Important APIs, Types, and Functions
`foo()` logs entry, waits one second with `delay(1)`, logs exit, and returns `Void`. `main()` initializes platform/network state, schedules `foo()`, stops after `waitForAll`, and runs `g_network`.

## Control Flow
Startup creates the Flow network, starts `foo()`, enters the event loop, and stops when the actor completes.

## State and Persistence Behavior
No persistence. Runtime state is limited to Flow network globals and the local future vector.

## Dependencies and Integration Points
Includes Flow runtime, platform/TLS headers, `NativeAPI.actor.h`, and actor compiler support. Built as the `play` tutorial target and linked with `fdbclient`.

## Risks
As scratch-space boilerplate, accidental committed experiments are the main risk. There is no argument parsing or error handling.

## Test Signals
Build and run; expected output is `foo enter`, then after about one second `foo exit`, followed by clean shutdown.
