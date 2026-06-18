# sources/storage-engines/foundationdb/fdbclient/MultiVersionTransaction.cpp

## Purpose

`MultiVersionTransaction.cpp` implements the FoundationDB client-side multi-version client (MVC) bridge. It lets the loaded client API use either the built-in local client or dynamically loaded `fdb_c` client libraries, and it can switch an active database or transaction to a client whose protocol version matches the connected cluster. The file also wraps external C API symbols behind C++ `IClientApi`, `IDatabase`, and `ITransaction` interfaces, manages external network threads, persists options across database replacement, updates shared client state for compatible clusters, exposes client status JSON, and contains unit tests for environment option parsing and `ThreadFuture` bridge behavior.

The file deliberately rejects dependencies on the native API actor header with a preprocessor error, because the multi-version layer must remain a boundary around the local and dynamically loaded client APIs rather than being coupled to the native implementation.

## Important APIs, types, and functions

`throwIfError()` converts non-zero FoundationDB C API error codes into `Error` exceptions.

`DLTransaction` is the dynamic-library implementation of `ITransaction`. It forwards transaction operations to function pointers in `FdbCApi`, including reads, ranges, mapped ranges, versionstamp, estimated size, split points, conflict ranges, writes, watches, commit, committed version, throttling/cost/size metrics, options, `onError`, reset, and cancel. Unsupported newer C symbols return or throw `unsupported_operation()`. Future-producing C API calls are converted to `ThreadFuture<T>` through `toThreadFuture`, with callbacks extracting values from the C future.

`DLDatabase` is the dynamic-library implementation of `IDatabase`. It wraps an `FDBDatabase*`, supports legacy asynchronous database creation for pre-6.1 clients, creates `DLTransaction` instances, forwards database options and management APIs, exposes protocol monitoring, shared-state APIs, busyness, and client status, and destroys the external database pointer in its destructor.

`DLApi` is an `IClientApi` implementation backed by a loaded external `fdb_c` shared library. `init()` loads all required and optional symbols into `FdbCApi`, using `loadClientFunction()` and the selected header/API version to decide which functions are mandatory. It handles version selection, future protocol opt-in, network setup/run/stop, database creation, legacy cluster/database creation, and network completion hooks.

`MultiVersionTransaction` is an `ITransaction` wrapper over the currently selected underlying transaction. It stores persistent transaction options, sensitive persistent options, an active `TransactionInfo`, and timeout state for the period when no matching database/transaction exists. `executeOperation()` either forwards the operation to the active transaction and aborts it when the database changes, returns a database initialization error, or waits on a timeout/on-change future until a compatible database appears.

`MultiVersionDatabase` is an `IDatabase` wrapper over `DatabaseState`. It creates `MultiVersionTransaction`, persists database and transaction-default options, forwards management APIs through `executeOperation()`, monitors main-thread busyness across local and external clients, delegates server protocol monitoring to the current version monitor database, and builds a combined MVC/native client status document.

`MultiVersionDatabase::DatabaseState` owns the mutable connection state: active `IDatabase`, `ThreadSafeAsyncVar` used to notify transactions of database replacement, connection record, cluster ID, version monitor database, initialization state/error, monitor futures, protocol version, available clients by normalized protocol version, saved options, default transaction options, and an option mutex. Core methods are `addClient()`, `monitorProtocolVersion()`, `protocolVersionChanged()`, `updateDatabase()`, `setDatabase()`, `getInitializationError()`, `getClientStatus()`, and `close()`.

`MultiVersionApi` is the global multi-version `IClientApi` facade (`MultiVersionApi::api`). It owns the local client, configured external client descriptions, loaded per-thread external clients, network setup state, bypass/local-disable flags, API version, thread count, temp directory, trace option state, cached network options, environment-option state, and a cluster shared-state map. It implements option parsing and forwarding, external library/directory registration, per-thread library copying, setup/run/stop network, database creation, supported-version publication, shared-state update/clear, and external-client iteration.

`ClientInfo` stores per-client metadata and behavior: library path, whether it is external, future-version flag, parsed protocol version, release version, API pointer, failure flag, initialization flag, and thread index. `loadVersion()` parses `fdb_get_client_version()`, `canReplace()` selects a preferred client for duplicate normalized protocol versions, and `getTraceFileIdentifier()` builds per-version/per-thread trace identifiers.

`ClusterConnectionRecord` normalizes database creation from either a cluster file or a connection string and provides a traceable string representation.

`parseOptionValues()` decodes path-separator-delimited environment variable option values with backslash escaping. `loadEnvironmentVariableNetworkOptions()` applies `FDB_NETWORK_OPTION_<NAME>` values once, tracks multi-value options already set, and wraps failures as `environment_variable_network_option_failed()`.

## Control flow

External client loading starts when MVC network options name a library or directory. `addExternalLibrary()` and `addExternalLibraryDirectory()` validate paths, record `ClientDesc` entries, and ensure at least one external client thread. On Unix, `copyExternalLibraryPerThread()` either uses the original library for a single thread or copies it into `tmpDir` once per thread with `mkstemp`, `open`, `read`, and `write`; copied libraries can be unlinked immediately after load unless retention is requested. Windows rejects more than one client thread.

`MultiVersionApi::selectApiVersion()` initializes the local client if needed, enforces one selected API version, and delegates version selection to the local API. Network setup first loads environment options unless the call is already for an external client. `setupNetwork()` locks setup state, handles bypass mode when no external clients are configured, disables the local client for multiple client threads, chooses an external-client transport ID, sets up the local network, creates `ClientInfo` objects for external library copies, loads local and external versions, selects API versions on external clients, optionally enables future protocol versions, forwards cached options, sets external transport and trace identifiers, starts external networks, validates that at least one usable client exists when local is disabled, clears cached setup options, and publishes supported versions.

`runNetwork()` starts one external network thread per usable external client, names threads from release version and thread index, runs the local network on the caller thread, waits for external threads after local shutdown, and closes tracing. `stopNetwork()` stops the local client first, then all external clients; under address sanitizer it sleeps briefly to allow pending external cleanup callbacks to run before stopping external networks. Network completion hooks are registered with local and external clients after setup.

Database creation requires the network to be set up. If the local client is disabled, `createDatabase()` round-robins an external thread index for the `MultiVersionDatabase`, creates a local database only for version monitoring, and starts without an active matching database. If bypass mode is active, it returns the local database directly. Otherwise it returns a `MultiVersionDatabase` seeded with a local version monitor database and no active external database until the protocol monitor chooses a client.

`MultiVersionDatabase` construction seeds `DatabaseState`, optionally adds the local and external clients available on the selected thread, initializes some external clients by creating and discarding a database on all threads for clients with close-unused-connection support, and starts `monitorProtocolVersion()` on the main thread.

`DatabaseState::monitorProtocolVersion()` calls `versionMonitorDb->getServerProtocol(expected)`. If the call fails during initialization with a fatal error, the state becomes `INITIALIZATION_FAILED` and `dbVar` is set to empty to wake pending operations. If it succeeds, `protocolVersionChanged()` runs on the main thread. That method keeps the same active database when the normalized protocol version is compatible, otherwise clears the shared-state map entry for the old protocol version, finds a client matching the new normalized protocol, marks the database incompatible if none exists, creates a new database with the selected client, and either waits for legacy external `DLDatabase::onReady()` or calls `updateDatabase()` immediately.

`updateDatabase()` reapplies saved database options to the new database, failing that client and dropping the database if an option cannot be set. It chooses the version monitor database: the new database when stable interfaces are available, or a newly created local database otherwise. When the API supports cluster shared-state maps, it asynchronously updates or reuses shared state and only then calls `setDatabase(newDb)`; otherwise it sets the database immediately. It cancels and restarts protocol monitoring after every update.

`MultiVersionTransaction` snapshots the current database async var into `TransactionInfo`. Reads, ranges, commits, watches, metrics, and most future-returning operations use `executeOperation()`. Mutating void operations such as `set`, `clear`, and conflict range additions forward only if an underlying transaction exists. `onError()` has special handling for `cluster_version_changed`: it refreshes the underlying transaction and treats that as retryable independently of the original error. `reset()` clears transaction-local persistent options, cancels timeout-only waiters with `transaction_cancelled`, restores database default transaction options, and refreshes the transaction.

Timeout handling covers the important gap where a transaction object exists before a compatible database does. Setting the transaction `TIMEOUT` option stores a timer actor via `onMainThread(timeoutImpl)`, keyed to transaction start time. Pending operations without an active transaction receive a future from `makeTimeout()`; the timeout promise is completed with `transaction_timed_out()`, or with `transaction_cancelled()` on reset/destruction. When a real transaction appears and the timeout option is applied to it, MVC cancels the local timeout actor.

## State and persistence behavior

The file persists client selection and option state in memory rather than on disk. `MultiVersionApi` keeps network options until external clients are initialized, tracks environment values already applied, stores external client descriptions by filename, and stores loaded per-thread clients by filename. `MultiVersionDatabase::DatabaseState` persists database options and transaction default options so that replacement databases and new transactions preserve user-visible behavior across protocol-version changes. `MultiVersionTransaction` persists transaction options only when the selected API version supports persistent options; sensitive options are stored in `WipedString`.

The cluster shared-state map is process-global MVC state keyed by cluster ID and protocol version. `updateClusterSharedStateMapImpl()` creates a shared state object for the first connection to a cluster/protocol pair, or waits for and installs an existing shared state on subsequent databases. `clearClusterSharedStateMapEntry()` removes and releases the entry only when the expected protocol version matches, avoiding races with other database instances that may already have upgraded.

Thread-safety is provided with `Mutex`, `ThreadSpinLock`, `ThreadSafeAsyncVar`, atomics, and main-thread dispatch. Database replacement uses `ThreadSafeAsyncVar<Reference<IDatabase>>` as both the current database holder and the abort signal for operations using an old database. Timeout variables are guarded separately by `timeoutLock`.

## Dependencies and integration points

The implementation depends on `IClientApi`, `FDBTypes`, generated FDB option metadata, `GenericManagementAPI`, `MultiVersionAssignmentVars`, `ClientVersion`, `LocalClientAPI`, `VersionVector`, Flow threading primitives, network primitives, platform dynamic library functions, protocol version helpers, JSON Spirit, and unit-test macros.

It integrates with the C API through `FdbCApi` function pointers and with the local client through `getLocalClientAPI()`. It integrates with cluster compatibility through `ProtocolVersion`, `ClientVersionRef`, and `databaseGetServerProtocol`. It integrates with management surfaces through reboot, force recovery, snapshot, shared state, client status, busyness, supported-client-version reporting, and trace identifiers. It also integrates with Flow futures through `ThreadFuture`, `ThreadSingleAssignmentVar`, `onMainThread`, `safeThreadFutureToFuture`, `abortableFuture`, `mapThreadFuture`, and `flatMapThreadFuture`.

## Risks and edge cases

Dynamic symbol loading is version-sensitive. A required symbol missing for the selected header/API version throws `api_function_missing()`, while optional symbols degrade to `unsupported_operation()`. Incorrect version gating can make newer features fail at runtime or require symbols that older clients do not expose.

Memory ownership is subtle. C future result buffers are wrapped as `StringRef`, `KeyRef`, `RangeResultRef`, and related types whose backing memory belongs to the C future. Correct behavior depends on `toThreadFuture` preserving result lifetime until copied or consumed. Shared-state clearing manually decrements a reference obtained from a future result, so protocol/version checks are important.

Concurrency and shutdown are high-risk. External client libraries can run on multiple threads, callbacks may run on main or external threads depending on options, and shutdown must tolerate in-flight cleanup callbacks. `DatabaseState::close()` cancels monitors on the main thread to break reference cycles. Transaction operations must abort on database replacement to avoid completing against an obsolete client.

Option persistence can change failure modes. Reapplying a database option to a replacement client can fail after a cluster version change, causing that client to be marked failed and supported versions to be republished. Transaction `TIMEOUT` is special because it must be honored even when no underlying transaction exists.

Bypass and local-disable options interact with setup state. Several network options are invalid after setup or when incompatible flags have already been set. Multiple client threads disable local client use and are unsupported on Windows. Environment option parsing supports escaping only for backslash and the platform path separator; malformed escape sequences become invalid option values.

## Test signals

Unit tests in this file cover environment variable option parsing (`/fdbclient/multiversionclient/EnvironmentVariableParsing`), abortable single-assignment variables, dynamic-library single-assignment variable callbacks with both main-thread and external-thread callback modes, mapped thread futures, and flat-mapped thread futures. These tests exercise cancellation, callback, memory-release, and error-propagation behavior that MVC relies on.

Broader runtime coverage is likely through multi-version client integration tests, cluster upgrade/downgrade tests, external client loading tests, and management API tests. High-value additional signals for this file would include explicit tests for protocol-version replacement with persistent transaction/database options, cluster shared-state map reuse and clearing, unsupported optional C symbols, local-disabled external-only setup, and environment-derived external client libraries.
