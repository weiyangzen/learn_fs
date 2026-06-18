# sources/storage-engines/rocksdb/include/rocksdb/utilities/stackable_db.h

## Purpose
Base forwarding wrapper for DB decorators such as TTL and transaction DBs. It lets wrappers override selected methods while forwarding most of the `DB` API to an underlying DB.

## Important APIs, Types, And Functions
Constructors support raw sole ownership, shared ownership, and moved unique ownership. `GetBaseDB` and `GetRootDB` expose wrapper layering. The class overrides a broad DB surface for CF lifecycle, reads/writes, iterators, ingestion, properties, compaction, WAL/flush, metadata, tracing/replay, options, and recovery helpers.

## Control Flow, State, And Persistence
Methods simply delegate to `db_`. The destructor deletes the raw DB when no shared owner exists, otherwise asserts the shared pointer matches. The wrapper itself persists no state; all durable behavior is from the underlying DB.

## Dependencies And Integration Points
Depends on `rocksdb/db.h`. Used by `DBWithTTL`, `TransactionDB`, `OptimisticTransactionDB`, and other wrappers.

## Risks And Edge Cases
Raw ownership can double-delete if misused. New `DB` virtual methods must be forwarded or wrapper behavior can diverge. Subclasses may accidentally inherit direct forwarding for methods they needed to intercept. Outstanding handles/iterators still follow underlying DB lifetime rules.

## Test Signals
Cover constructor/destructor ownership, `GetBaseDB`/`GetRootDB`, representative forwarding, subclass overrides, close behavior, and API coverage for new DB methods.
