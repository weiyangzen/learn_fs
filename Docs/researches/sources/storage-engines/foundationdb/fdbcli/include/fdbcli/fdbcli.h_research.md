# sources/storage-engines/foundationdb/fdbcli/include/fdbcli/fdbcli.h

## Purpose

`fdbcli.h` is the shared command interface for fdbcli. It declares command registration types, common special keys, shared utility functions, bulk operation formatting/analysis helpers, worker discovery, status printing, and actor prototypes for every CLI command.

## Important APIs, Types, and Functions

- `CommandHelp` stores usage, short description, and long description.
- `CommandFactory` registers visible commands, hidden commands, completion generators, and hint generators in static maps.
- `arrayGenerator`, `tokencmp`, `printUsage`, `printLongDesc`, `getSpecialKeysFailureErrorMessage`, `getWorkers`, `getStorageServerInterfaces`, and `getWorkerInterfaces` are shared command helpers.
- Special-key declarations include management, exclusion, maintenance, process class, lock, and worker-interface keys.
- Bulk utilities include `validateBulkJobId`, `getBulkOwnerSuffix`, `formatBytesProgress`, progress/task breakdown printing, health/error/optimization analysis types, and `printBulkAnalysis`.
- Actor prototypes define the cross-file dispatch contract used by `fdbcli.cpp`.

## Control Flow

Command source files instantiate `CommandFactory` at static initialization time. `fdbcli.cpp` later calls `initHelp` for built-ins, consults `CommandFactory::commands()` for known command validation/help, and dispatches actors based on the first token. Completion and hint generators are looked up through the `CommandFactory` maps.

## State and Persistence Behavior

The header itself does not persist data. It defines process-local static registries for command metadata. The declared actor APIs may mutate cluster state depending on command semantics. Inline special-key constants such as `errorMsgSpecialKey` and `workerInterfacesVerifyOptionSpecialKey` identify system metadata locations used by utility functions.

## Dependencies and Integration Points

The header includes `FlowLineNoise`, bulk loading, coordination, management API, client API, status client, storage server interface, and Flow arena definitions. It is the main coupling point between the monolithic dispatcher and independently implemented command files.

## Risks and Edge Cases

Static registration depends on linked translation units; a command file not linked into the executable will silently omit its `CommandFactory`. Adding a new command requires both a prototype here and a dispatch branch in `fdbcli.cpp` unless the dispatcher is refactored. The visible command registry and hidden command set are mutable global state.

## Test Signals

The integration test suite exercises many declarations indirectly by invoking built-in and registered commands. Help text, completion, and bulk analysis declarations are less directly covered. Compile/link failures are the primary signal for prototype mismatches between this header and command implementations.
