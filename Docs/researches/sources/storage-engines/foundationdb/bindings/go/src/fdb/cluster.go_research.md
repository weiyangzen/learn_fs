# sources/storage-engines/foundationdb/bindings/go/src/fdb/cluster.go

## Purpose

`cluster.go` preserves the deprecated `Cluster` API for older users of the FoundationDB Go bindings. It provides a lightweight cluster handle that can open the default database, while directing new users toward `OpenDatabase` or `OpenDefault`.

## Important APIs, Types, and Functions

`Cluster` stores a `clusterFileName`. `Cluster.OpenDatabase(dbName []byte)` calls `Open(c.clusterFileName, dbName)` and documents that the database name must be `[]byte("DB")`. Both the type and method are marked deprecated in comments.

## Control Flow

There is no complex flow. Callers holding a `Cluster` call `OpenDatabase`, which delegates to the newer `Open` helper in `fdb.go`, returning a `Database` and error.

## State and Persistence Behavior

`Cluster` is an immutable lightweight value containing only the cluster file name. It does not own a C pointer or persistent resource in this file. Actual database handles and lifecycle state are created by `Open`.

## Dependencies and Integration Points

The file depends on package-local `Open`, `Database`, and FoundationDB database naming conventions. It integrates with legacy API consumers while keeping the implementation centralized in modern open helpers.

## Risks

The API is deprecated and should not gain new behavior. The `dbName` contract is documented but not checked in this wrapper; validation is delegated to `Open`/the C API. Any removal would be a compatibility break for older binding users.

## Test Signals

Compatibility tests should confirm `Cluster.OpenDatabase([]byte("DB"))` still opens a database equivalently to the direct open helpers. New behavior should be tested through `OpenDatabase`, `OpenDefault`, and `Open` rather than this shim.
