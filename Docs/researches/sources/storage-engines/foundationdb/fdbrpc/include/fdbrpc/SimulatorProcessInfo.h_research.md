## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorProcessInfo.h

Purpose: Defines per-process simulation metadata used by the simulator to represent a Flow/FDB process, its network listeners, locality, metrics, fault state, globals, and shutdown signaling.

Important APIs/types/functions: `simulator::ProcessInfo` stores names/folders, machine pointer, addresses, locality, starting class, TD/metric/chaos/histogram collections, listeners, UDP sockets, failed/excluded/cleared/rebooting flags, network connection provider, fault-injection probabilities, disk failure state, UID, protocol version, child processes, and a shutdown `Promise<KillType>`. Methods include `onShutdown()`, `isSpawnedKVProcess()`, `isReliable()`, `isAvailable()`, `isExcluded()`, `isCleared()`, `getReliableInfo()`, `isAvailableClass()`, `getListener()`, process-local global get/set, and `toString()`.

Control flow: Constructor initializes identity and default reliability state. Availability is derived from exclusion plus reliability. `isAvailableClass()` permits only classes suitable for stateful roles. `global()` and `setGlobal()` implement process-local global storage by numeric ID.

State and persistence behavior: This is in-memory simulation state. Data and coordination folder strings point to simulated/real filesystem locations used by simulator implementations. Shutdown is signaled asynchronously with a kill type.

Dependencies and integration points: Depends on network/listener/socket interfaces, metrics, chaos metrics, histograms, `Locality`, machine/kill type headers, deterministic random, and protocol versions. Used by `ISimulator` and simulation fault policies.

Risks: Reliability combines process and machine fault injection; missing machine linkage can change behavior. `getListener()` asserts if the address is not registered. Process globals are untyped `flowGlobalType`, so ID ownership must be consistent. `isAvailableClass()` must stay aligned with role assignment rules.

Test signals: Process construction, shutdown futures, stateful class filtering, fault injection reliability, exclusion/cleared flags, listener registration lookup, child process tracking, global storage, and formatted process description.
