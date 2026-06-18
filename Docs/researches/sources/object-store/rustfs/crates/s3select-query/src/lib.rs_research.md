# sources/object-store/rustfs/crates/s3select-query/src/lib.rs

## Purpose
This is the query crate root. It exports submodules and provides public helpers for creating global cached or fresh S3 Select database instances.

## Important APIs, Types, And Functions
It exports `data_source`, `dispatcher`, `execution`, `function`, `instance`, `metadata`, and `sql`. `GlobalComponents` caches the function manager, parser, execution factory, and default table provider in a `LazyLock`. `get_global_db(input, enable_debug)` creates a DBMS using cached components. `create_fresh_db()` creates a test DBMS with a default CSV Select input.

## Control Flow
The global cache initializes default function manager, parser, cascade optimizer, local scheduler, execution factory, and table provider once. Each `get_global_db` call passes the request input and cached components to `make_rustfsms_with_components`.

## State And Persistence Behavior
Global state is process-local and immutable after `LazyLock` initialization. Per-request DB instances are still constructed, but expensive reusable components are shared. No durable state is written.

## Dependencies And Integration Points
It is the public entry point used by S3 Select handlers and tests. It depends on API `DatabaseManagerSystem`, `SelectObjectContentInput`, the local component implementations, and `std::sync::LazyLock`.

## Risks And Edge Cases
`enable_debug` is passed as `is_test`, so naming can be misleading: true selects in-memory fixtures instead of production storage. Shared function manager state is immutable through `Arc`; dynamic UDF registration after startup is not supported by this path.

## Test Signals
Integration and error-handling tests use `get_global_db` extensively and `create_fresh_db` for fresh instance creation.
