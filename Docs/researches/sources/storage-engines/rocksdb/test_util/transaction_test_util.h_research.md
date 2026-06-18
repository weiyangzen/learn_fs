# sources/storage-engines/rocksdb/test_util/transaction_test_util.h

Purpose: declares `RandomTransactionInserter`, a reusable class for transaction stress tests that validate an equal-sum invariant across sets of keys.

Important APIs: constructor accepts randomness, write/read options, number of keys, number of sets, commit delay, and first transaction ID. Public insert methods target `TransactionDB`, `OptimisticTransactionDB`, or plain `DB`. Static `DBGet()` reads one formatted key. Static `Verify()` checks the invariant. Accessors expose last status, success/failure counts, and inserted byte totals. `RollbackDeletionTypeCallback()` returns whether a key's set uses `SingleDelete` during rollback testing.

State behavior: stores input options, mutable `ReadOptions` snapshot pointer during transaction inserts, counters, last status, reusable transaction pointers, and commit delay.

Dependencies/integration: includes RocksDB transaction DB public APIs and port utilities; forward declares `DB` and `Random64`.

Risks and test signals: not a general-purpose data generator; it assumes an initially empty DB and set prefixes from 0001 to 9999. Tests should check key formatting, deletion callback consistency with implementation, counter updates, and verification under both transactional and non-transactional writes.
