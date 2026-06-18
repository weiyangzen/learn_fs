# sources/storage-engines/rocksdb/java/rocksjni/transaction_db_options.cc

## Purpose
This file exposes C++ `TransactionDBOptions` fields to Java `TransactionDBOptions`. It is a thin native options bridge for lock table sizing, lock timeout behavior, and write policy.

## Important APIs, Types, and Functions
Exports include `newTransactionDBOptions`, getters and setters for `max_num_locks`, `num_stripes`, `transaction_lock_timeout`, `default_lock_timeout`, and `write_policy`, plus `disposeInternalJni`. The write policy conversion uses `TxnDBWritePolicyJni::toJavaTxnDBWritePolicy` and `toCppTxnDBWritePolicy`.

## Control Flow
The constructor allocates a new `TransactionDBOptions` and returns its pointer. Each getter casts the Java handle and returns a field value. Each setter casts the handle and directly assigns a C++ field. Disposal deletes the native options object.

## State and Persistence Behavior
The file only mutates an in-memory options object. These options affect future `TransactionDB::Open` behavior but are not persisted by this bridge. The Java wrapper owns the allocated native options handle until disposal.

## Dependencies and Integration Points
It depends on the generated `org_rocksdb_TransactionDBOptions` header, RocksDB transaction DB utilities, pointer conversion helpers, and portal enum conversion helpers. It is consumed by Java `TransactionDBOptions` and by `transaction_db.cc` open calls.

## Risks and Edge Cases
There is no range validation in JNI; Java must validate or RocksDB must tolerate invalid lock counts, stripe counts, and timeout values. Write policy byte conversion depends on Java and portal enum mappings remaining synchronized. Passing a disposed or null handle would lead to undefined native behavior.

## Test Signals
Tests should verify round-trip getters/setters, enum conversion for all write policies, disposal behavior through Java ownership, and that configured options affect `TransactionDB.open` behavior where observable, such as lock timeout behavior.
