# sources/storage-engines/foundationdb/bindings/go/src/fdb/database.go

## Purpose

`database.go` implements the Go binding `Database` handle and database-level operations. It wraps the FoundationDB C API pointer, exposes database options, creates transactions, implements retrying transactional helpers, surfaces management/status APIs, and provides locality boundary-key lookup.

## Important APIs, Types, and Functions

`Database` is a copyable concurrent-safe handle containing cache metadata and an embedded `*database` with `*C.FDBDatabase`. `DatabaseOptions` wraps database option setting through `setOpt`. `Close` removes cached handles and destroys the C database pointer. `CreateTransaction` calls `fdb_database_create_transaction`, wraps the pointer in a Go transaction, and installs a finalizer because futures can extend transaction lifetime.

Management methods include `RebootWorker`, `GetClientStatus`, and `GetMainThreadBusyness`. `retryable` is the shared retry loop used by `Transact` and `ReadTransact`; it recognizes wrapped `fdb.Error` values, calls `OnError`, and retries until success or non-retryable error. `Transact` creates one transaction, runs the user function, commits on nil error, and recovers panicked FDB errors. `ReadTransact` is the read-only equivalent without commit. `LocalityGetBoundaryKeys` reads system keyspace to expose storage-server boundary keys.

## Control Flow

Callers generally obtain a `Database`, then call `Transact` or `ReadTransact`. Each helper creates a transaction once and passes a closure to `retryable`. On retryable failure, the transaction’s `OnError` resets it for the next loop. `Transact` commits after the user callback if no error was returned; `ReadTransact` returns after the callback without commit.

Direct C API wrappers create the appropriate future wrapper, call `Get`, and translate special cases. For example, `GetClientStatus` returns `ErrAPIVersionUnset` before API selection and `ErrMultiVersionClientUnavailable` when the C future returns an empty byte slice.

## State and Persistence Behavior

`Database` owns a C database pointer until `Close`. Cached database tracking is maintained outside this file via `openDatabases`. Transactions created from the database mutate persistent FoundationDB state only when committed. `Transact` and `ReadTransact` deliberately warn callers not to return futures because transaction finalization can cancel outstanding work after the helper returns.

`LocalityGetBoundaryKeys` reads from `\xFF/keyServers/` using system-key options and strips the system prefix from returned keys. It does not mutate user data.

## Dependencies and Integration Points

The file depends on cgo and `foundationdb/fdb_c.h`, package-local transaction/future/error helpers, API version state, open database cache, and option code generation. It is the central integration point between Go callers and FDB C database handles.

## Risks

`Close` must be called exactly once and callers must avoid using the database afterward. Finalizer-based transaction destruction is subtle and depends on futures becoming unreachable. Returning futures from transaction closures can produce canceled reads and missed retry handling. `RebootWorker` comments note that immediately closing the database may prevent asynchronous reboot commands from being delivered. `LocalityGetBoundaryKeys` assumes the system key prefix length when slicing returned keys.

## Test Signals

Tests should exercise transaction retries for returned and panicked `fdb.Error`, commit errors, read-only retries, option setting, database close/cache behavior, client status with and without multi-version support, worker reboot error handling, and locality boundary key reads under system-key permissions.
