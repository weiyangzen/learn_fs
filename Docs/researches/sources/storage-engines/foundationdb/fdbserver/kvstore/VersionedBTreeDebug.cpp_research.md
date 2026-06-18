# sources/storage-engines/foundationdb/fdbserver/kvstore/VersionedBTreeDebug.cpp

## Purpose
This file provides the runtime side of Redwood/VersionedBTree debug controls declared in `VersionedBTreeDebug.h`. It centralizes whether verbose debug printing is enabled, which process address is allowed to emit debug lines, the active debug time window, the output stream, and the simulation-only XOR-encryption compatibility knob.

## Important APIs, Types, And Functions
`enableRedwoodDebug()` is the only exported function implemented here. It checks global `g_debugEnabled`, `g_debugStart`, `g_debugEnd`, and `g_debugAddress` against `now()` and `g_network->getLocalAddress()`. The file also defines `g_debugStream = stdout` and `g_allowXOREncryptionInSimulation = true`.

## Control Flow
Debug macros call `enableRedwoodDebug()` before printing when `REDWOOD_DEBUG` is compiled in. The function returns true only when global debug is enabled, the current Flow time is inside the configured interval, and either local or target network address is invalid or both addresses match.

## State And Persistence Behavior
All state is process-global and in-memory. No persistent configuration is read or written. The output stream is a raw `FILE*`, so debug output durability depends on the target stream and the caller macro flushing it.

## Dependencies And Integration Points
The implementation depends on Flow globals from `flow/flow.h`, especially `now()` and `g_network`. It is consumed by Redwood/VersionedBTree debug macros and by simulation tests that need the XOR encryption switch.

## Risks And Test Signals
The defaults enable debug filtering but compile-time `REDWOOD_DEBUG` normally removes debug statements. Global mutable state is not synchronized, and `g_network` access assumes Flow network initialization. Tests should exercise address/time filtering and confirm debug macros compile both when debugging is enabled and compiled out.
