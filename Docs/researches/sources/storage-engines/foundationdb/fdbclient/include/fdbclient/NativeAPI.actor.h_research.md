# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/NativeAPI.actor.h

## Purpose
`NativeAPI.actor.h` declares the native FoundationDB client entry points for network setup, database handles, non-RYW transactions, watch state, retry state, storage metric helpers, checkpoint helpers, and several administrative actors. It is the core public/internal header that ties Flow actors, RPC-facing client metadata, FDB option validation, tracing, transaction logging, and commit proxy requests into a single transaction API.

## Important APIs, Types, And Functions
- `NetworkOptions` stores global client/network configuration: cluster file, trace output settings, supported client versions, role flags, profiling, and client knob overrides.
- `Database` wraps `Reference<DatabaseContext>` and exposes factory methods for connection records, cluster files, simulated databases, direct context ownership, transaction defaults, and a coroutine-style `run()` retry loop.
- `TransactionOptions` captures per-transaction switches such as priority, retry backoff, GRV flags, raw/system access, lock awareness, cost accounting, conflict reporting, GRV cache behavior, storage quota bypass, and tag sets.
- `TransactionLogInfo` buffers structured client log events and can emit them to trace logs, database log mutation payloads, or both.
- `Watch` models key watches with old and set values, trigger promises, underlying watch future, and optional read options.
- `TransactionState` owns read version state, metadata version, auth token, transaction options, tracing span context, provisional proxy selection, commit version, conflicting-key map, cost counters, idempotency state, and start/read-version actors.
- `Transaction` is the native transaction facade: reads (`get`, `getKey`, range, mapped range, stream), conflict ranges, writes, atomic ops, watches, commit, retry (`onError`), option setting, versionstamp, protocol version, cost/throttle metrics, reset, logging, span and transaction IDs, and conflict range inspection.
- Free functions cover network lifecycle (`setNetworkOption`, `setupNetwork`, `runNetwork`, `stopNetwork`), integer option parsing, snapshots, checkpoints, safe exclusions, storage wiggle control, key size limits, storage metrics, split points, worker interface discovery, server class discovery, key location lookup, and transaction refresh.

## Control Flow And State
`Database::run()` constructs a `Transaction`, repeatedly awaits any prior `onError`, runs the caller function, and retries on `Error` by assigning `tr.onError(e)` to the next loop. `Transaction::getReadVersion()` lazily creates `TransactionState::readVersionFuture`; range/read APIs feed through private templated `getRangeInternal` implementations. Commit state is tracked with `CommitTransactionRequest tr`, `commitResult`, `committing`, watches, and `extraConflictRanges`. `reset()` and `fullReset()` rebuild transaction state, while `cloneAndReset()` lets `TransactionState` preserve selected options/logging and optionally generate a new tracing span.

## Persistence And External State
This header declares the structures that become persistent mutations: commit requests, read/write conflict ranges, watches, versionstamp promises, transaction logs, checkpoint metadata writes, storage wiggle configuration writes, and snapshot requests. `TransactionLogInfo` serializes log events with `BinaryWriter`. `createCheckpoint()` inserts mutations so each overlapping shard creates a checkpoint at commit version. `snapCreate()` requests a cluster-wide coordinator/TLog/storage snapshot. Persistent transaction defaults are inherited from `DatabaseContext`.

## Dependencies And Integration Points
It depends heavily on Flow (`Future`, `Promise`, actors, tracing, metrics), `FDBTypes`, option enums, commit proxy interfaces, cluster/coordination interfaces, key range maps, client log events, `ReadYourWritesTransaction` forward declarations, storage checkpoint types, and client knobs. It integrates with commit proxies, GRV proxies, storage servers, data distribution, transaction tracing, network setup, and the actor compiler (`actorcompiler.h`/`unactorcompiler.h`).

## Risks And Edge Cases
The API surface is central and option-heavy; adding an option requires updating reset/clear behavior and option propagation. Transaction retry lambdas must be idempotent. Watch cancellation and commit futures must be settled on all error paths. `TransactionState::readVersion()` asserts readiness, so callers must not bypass the future lifecycle. `TransactionLogInfo` can silently stop accumulating database logs after flush. Key size helpers distinguish system, raw, read, write, and clear semantics; using the wrong helper can admit invalid operations or reject valid system operations.

## Test Signals
Relevant tests should exercise network lifecycle errors, retry/onError semantics, transaction options, read version caching, conflict range accounting, commit success and unknown-result paths, versionstamp fulfillment, watch setup/cancel, transaction log flushing, storage metric split helpers, safe exclusion calls, checkpoint creation/lookup, and system/raw key size boundaries. Simulation tests should cover buggified client failures, provisional proxy use, idempotent retry behavior, and trace/log side effects.
