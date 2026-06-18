# sources/storage-engines/foundationdb/fdbclient/ThreadSafeTransaction.cpp

## Purpose
`ThreadSafeTransaction.cpp` provides the thread-safe client API facade around `DatabaseContext` and `ReadYourWritesTransaction`. It lets foreign threads use database and transaction operations by copying inputs and scheduling the actual work on the FoundationDB network thread.

## Important APIs, types, and functions
`ThreadSafeDatabase` implements connection creation, `onConnected()`, transaction creation, database options, management operations, client status, shared state, busyness, and protocol queries. `ThreadSafeTransaction` wraps reads, ranges, mapped ranges, conflict ranges, mutations, watches, commit, version vector/span context/cost/versionstamp queries, options, deferred error checks, `onError()`, reset, debug trace, and debug print. `ThreadSafeApi` owns API version selection, client version string, network options/setup/run/stop, database creation, and network-thread completion hooks.

## Control flow
Foreign-thread methods copy `StringRef`, `KeyRef`, `KeyRangeRef`, selectors, and optional values into owning `Key`, `Value`, `Standalone`, or other safe objects, capture raw pointers, and call `onMainThread` or `onMainThreadVoid`. The network-thread lambda checks deferred errors where appropriate and delegates to the underlying `DatabaseContext` or `ReadYourWritesTransaction`. Constructors allocate objects on the calling thread when needed but run actual initialization on the network thread. Destructors defer reference release back to the network thread.

## State and persistence behavior
This file does not define database key layouts, but it can mutate database state through the underlying transaction methods. In-process state includes raw `DatabaseContext*`, raw `ReadYourWritesTransaction*`, an atomic initialization flag for committed-version safety, API version, external transport id, lazily built client version string, and registered network completion hooks.

## Dependencies and integration points
It depends on cluster connection records, `DatabaseContext`, `GenericManagementAPI`, `NativeAPI.actor.h`, Flow arenas/protocol versions, and option metadata. It is a major integration layer for the C API and other clients that call from threads outside the network thread.

## Risks and edge cases
The file explicitly warns that methods must not implicitly `addRef()` because users may share `Reference<ThreadSafe...>` across threads in limited ways. Lifetimes depend on network-thread ordering of deferred addref/delref calls. Returning `invalidVersion` from `getCommittedVersion()` before initialization avoids touching an unconstructed transaction. `clear(begin,end)` checks inverted ranges inside the network-thread lambda. `runNetwork()` captures errors, runs shutdown hooks with isolated error handling, and rethrows the original network error afterward. Completion hooks are protected by a mutex because they must be visible when registration returns.

## Test signals
No local tests are present. Useful tests include foreign-thread get/set/commit, option pass-through, deferred error propagation, destruction while initialization is pending, network shutdown hooks on normal and error termination, external transport id parsing, and invalid option handling.
