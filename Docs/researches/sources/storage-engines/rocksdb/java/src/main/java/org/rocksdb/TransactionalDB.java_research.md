# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalDB.java

## Purpose
`TransactionalDB` is a package-private generic interface for DB wrappers that can begin transactions. It unifies `TransactionDB` and optimistic transaction DB implementations behind a common Java test and usage contract.

## Important APIs and Types
It defines four `beginTransaction` overloads: with only `WriteOptions`, with transaction options, with an old `Transaction` for reuse, and with both transaction options and transaction reuse. The generic bound `T extends TransactionalOptions<T>` lets implementations accept either regular or optimistic transaction options.

## Control Flow, State, and Persistence
This file has no implementation state. Its control-flow role is contract enforcement: implementations allocate or reinitialize a `Transaction` and callers must close returned transaction objects.

## Dependencies and Integration Points
It depends on `AutoCloseable`, `WriteOptions`, `Transaction`, and `TransactionalOptions`. `AbstractTransactionTest.DBContainer` mirrors this contract at test level, allowing shared tests across transaction implementations.

## Risks and Test Signals
The principal risk is lifecycle ownership: callers must close transactions, and reuse overloads must safely reinitialize old native transaction handles. `AbstractTransactionTest` exercises begin/close patterns through try-with-resources, but reuse overload behavior is not covered in this subset.
