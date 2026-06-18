# sources/storage-engines/badger/doc.go

## Purpose
`doc.go` provides the package-level documentation for Badger. It describes Badger as an embeddable Go key-value database with MVCC, transactions, serializable snapshot isolation, and an LSM tree plus value-log architecture.

## Important APIs, Types, and Functions
This file declares only `package badger`; its main API surface is the package comment. It names the primary user-facing types: `DB`, `Txn`, `Item`, and `Iterator`.

## Control Flow and State
No executable control flow is present. The comment explains how operations happen through transactions and how read-only/read-write transactions interact with items and iterators.

## Persistence Behavior
The documentation explains the architectural persistence model: keys live in an LSM tree while values are separated into value logs to reduce write amplification and keep the LSM smaller.

## Dependencies and Integration Points
The package comment is consumed by Go documentation tooling and helps orient users before reading examples in `db_test.go`.

## Risks and Edge Cases
The documentation is high level and does not enumerate platform-specific locking differences, value-log GC behavior, or transaction API caveats such as item lifetime.

## Test Signals
No tests are attached to this file directly. Documentation examples in `db_test.go` provide executable usage validation for the documented API style.
