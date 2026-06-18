# sources/storage-engines/wiredtiger/src/conn/conn_handle.c

## Purpose
This file performs base initialization and destruction of `WT_CONNECTION_IMPL`. It wires together the connection's global queues, subsystem initialization, spinlocks/rwlocks, statistics, generation manager, block manager queue, and final teardown of connection-owned memory.

## Important APIs, Types, and Functions
`__wti_connection_init` initializes a newly allocated connection using `conn->default_session`. It sets up queue heads for data handles, libraries, data sources, file handles, disaggregated shared metadata operations, and pending crypt keys. It calls subsystem initializers for prefetch, tiered storage, I/O capacity, extensions, configuration, statistics, hot backup, and generations.

The same function initializes core locks: API, checkpoint, background compact, disaggregated shared metadata queue, pending crypt key, file handle list, metadata, reconfigure, schema, turtle file, log debug retention rwlock, dhandle rwlock, table rwlock, and block manager lock. It initializes the block manager queue and clears checkpoint timer stats.

`__wti_connection_destroy` removes the connection from the process global connection queue, discards config and free-on-close memory, destroys locks and subsystems in reverse-ish order, frees hash buckets and recovered checkpoint snapshot memory, releases config/debug/home/session/error-prefix allocations, discards connection stats, and finally frees the connection object.

## Control Flow and Behavior
Initialization is linear and returns on first failure through the `WT_RET`/`WT_DECL_RET` pattern. Queue heads are initialized before subsystems that may append to them. Lock initialization precedes subsystems that need shared synchronization. Capacity init/destroy are currently no-op wrappers but are still called as part of the lifecycle contract.

Destruction first handles a null connection defensively. It removes the connection from `__wt_process.connqh` under the process spinlock, then tears down connection-owned configuration, free-on-close entries, locks, disaggregated pending crypt keys, backup, prefetch, tiered storage, capacity, extensions, hash tables, snapshot memory, strings, session array, and stats. It assumes higher-level close has already stopped server threads and discarded open data handles.

## State and Persistence Behavior
The file initializes in-memory connection state only. Persistent files and metadata are owned by lower subsystems; this code creates the synchronization and collection roots they rely on. Destruction releases memory and locks but does not itself checkpoint or remove persistent data.

## Dependencies and Integration Points
This is a hub for connection lifecycle. It depends on initialization and destroy functions across prefetch, tiered, capacity, extensions, config, stats, backup, generation, and disaggregated subsystems. It also owns lock names used in diagnostics and lock tracking. `conn_dhandle.c`, `conn_compact.c`, `conn_capacity.c`, and disaggregated metadata code all rely on queues and locks initialized here.

## Risks
Ordering is the main risk. Destroying locks before subsystems that still use them can produce shutdown races. Failing midway through initialization leaves some resources initialized and others not; callers must only destroy what was successfully created or tolerate initialized-null patterns. The process connection queue removal must happen exactly once under `__wt_process.spinlock`.

Subsystem additions must update both init and destroy paths. Disaggregated storage adds several queue and lock fields here, so leaks or stale locks can surface during role transitions and shutdown rather than at the point of use.

## Test Signals
The strongest signals are clean connection open/close under sanitizers, repeated open/close with extensions, tiered/disaggregated/background compact/capacity enabled, and failure injection during initialization. Lock leak detectors, process connection queue assertions, and statistics discard checks are useful. Shutdown tests should verify no server thread or dhandle path uses destroyed connection locks.
