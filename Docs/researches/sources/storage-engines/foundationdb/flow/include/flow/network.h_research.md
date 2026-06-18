# sources/storage-engines/foundationdb/flow/include/flow/network.h

## Purpose
Declares the abstract Flow network/event-loop interface used by both real Net2 and simulation runtimes.

## Important APIs, Types, And Functions
`NetworkMetrics` tracks slow events, busyness, priority duration, disk stall/submit timing, and starvation. `NetworkInfo` holds metrics, alternatives failure timing, TLS throttling, and handshake lock. `IEventFD` abstracts eventfd reads. `INetwork` exposes clocks, delays/yields, task priorities, globals, stop callbacks, simulation/main-thread checks, thread creation, TLS init, disk bytes, local address helpers, sampling lineage set access, and `protocolVersion`. Globals are `g_network` and `newNet2`.

## Control Flow
Flow helpers dispatch through `g_network`; implementations schedule timers/yields, run the event loop, maintain global slots, and stop through `stop()`. Static local-address helpers call function pointers from network globals.

## State And Persistence Behavior
All state is runtime process state. Metrics may be exported but are not persisted here. `protocolVersion` drives serialization compatibility.

## Dependencies And Integration Points
Depends on protocol versioning, Swift annotations, network addresses, task priorities, random support, and sampling `WriteOnlySet`. Used by all Flow actors and implemented by Net2/simulation.

## Risks And Edge Cases
Many APIs assume initialized `g_network`. Untyped `global(id)` slots require enum/cast discipline. Deleting through `INetwork` is forbidden. Atomic metrics require explicit copy handling.

## Test Signals
Event-loop run/stop, delay ordering, yield priorities, simulated vs real clocks, TLS init, disk byte queries, local addresses, protocol version propagation, and busyness/starvation metrics.
