# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_update.h

Purpose: defines the lightweight record connecting a transaction to one table/key/update entry.

Important APIs and types: constructor `kv_transaction_update(const char *table_name, const data_value &key, std::shared_ptr<kv_update> &update)`, `key()`, `table_name()`, and `update()`.

Control flow: when a table adds an update for a transaction, the transaction stores a `kv_transaction_update` record. Later commit fixes timestamps through the update pointer, and rollback locates the table/key to remove the update chain entry.

State and persistence: stores table name as a string, key as a copied `data_value`, and shared pointer to `kv_update`. It intentionally avoids a table pointer because table ownership/lifetime and circular references are more complex.

Dependencies and integration: includes `data_value.h` and forward-declares `kv_update`. Owned by `kv_transaction` update lists and created by table write paths.

Risks: table name lookup during rollback/commit assumes the table still exists. Returning `update()` as a shared pointer can extend update lifetime. The constructor takes a shared pointer reference but stores a copy, so callers must still handle cycles.

Test signals: transaction commit/rollback tests implicitly cover this wrapper by verifying all touched keys have timestamps fixed or updates removed, especially multi-table transactions.
