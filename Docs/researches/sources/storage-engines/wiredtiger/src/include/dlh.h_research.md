# sources/storage-engines/wiredtiger/src/include/dlh.h

## Purpose
`dlh.h` defines the small connection-owned record used to track dynamically loaded extension libraries.

## Important APIs, Types, and Functions
`WT_DLH` stores a queue link, platform dynamic-library `handle`, library `name`, and optional `terminate(WT_CONNECTION *)` callback. There are no functions in this header.

## Control Flow
Extension loading code allocates one `WT_DLH` per opened library, links it into `WT_CONNECTION_IMPL::dlhqh`, stores the `dlopen`/platform handle, resolves callbacks, and later walks the queue during connection close to call `terminate` and unload the library.

## State and Persistence Behavior
The state is process-local and lasts for the connection lifetime. It does not persist to disk, but loaded extension names and termination callbacks affect connection shutdown and resource cleanup.

## Dependencies and Integration Points
It depends on queue macros and the public `WT_CONNECTION` type. It integrates with extension loading, named collator/compressor/encryptor/storage-source registration, and connection close cleanup.

## Risks and Edge Cases
Shutdown ordering matters: callbacks may depend on connection subsystems still being valid. Handles must not be unloaded while registered extension objects are still reachable. A missing or failing terminate callback needs to be handled by extension-management code outside this header.

## Test Signals
Extension load/unload tests, error-path tests for partially loaded extensions, and leak checks at connection close are the main signals. Mock extensions with terminate callbacks are useful.
