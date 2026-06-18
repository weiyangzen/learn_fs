# sources/storage-engines/badger/errors.go

## Purpose
`errors.go` centralizes exported Badger sentinel errors and one option limit constant. These errors define much of the public contract for invalid options, transaction misuse, missing keys, GC outcomes, encryption failures, platform support, and closed DB access.

## Important APIs, Types, and Functions
- `ValueThresholdLimit`: max permissible `Options.ValueThreshold`, derived from `math.MaxUint16 - 16 + 1`.
- Public sentinel errors include `ErrKeyNotFound`, `ErrTxnTooBig`, `ErrConflict`, `ErrReadOnlyTxn`, `ErrDiscardedTxn`, `ErrEmptyKey`, `ErrInvalidKey`, `ErrBannedKey`, `ErrThresholdZero`, `ErrNoRewrite`, `ErrRejected`, `ErrManagedTxn`, `ErrNamespaceMode`, `ErrInvalidDump`, `ErrZeroBandwidth`, `ErrWindowsNotSupported`, `ErrPlan9NotSupported`, `ErrTruncateNeeded`, `ErrBlockedWrites`, `ErrNilCallback`, `ErrEncryptionKeyMismatch`, `ErrInvalidDataKeyID`, `ErrInvalidEncryptionKey`, `ErrGCInMemoryMode`, `ErrGCInReadOnlyMode`, and `ErrDBClosed`.

## Control Flow and State
There is no runtime control flow beyond package initialization of error values. Because these are sentinel `errors.New` values, callers and tests can compare with `==` where errors are not wrapped, or inspect wrapped messages in platform paths.

## Persistence Behavior
No direct persistence. Errors such as `ErrTruncateNeeded`, `ErrEncryptionKeyMismatch`, and `ErrInvalidDataKeyID` are part of persistence and recovery workflows elsewhere.

## Dependencies and Integration Points
Used across DB opening, transactions, iterators, value-log GC, namespace filtering, encryption/key registry, stream/load APIs, and platform directory locking. Depends only on stdlib `errors` and `math`.

## Risks and Edge Cases
Changing error text can break tests and user code that matches strings. Wrapping sentinel errors with context may affect direct equality unless the caller uses `errors.Is` where supported by the wrapper type.

## Test Signals
Many tests assert these errors: missing keys, read-only transactions, invalid keys, banned prefixes, platform read-only support, GC modes, and encryption mismatch.
