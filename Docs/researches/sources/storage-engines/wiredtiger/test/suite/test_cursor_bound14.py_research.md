## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound14.py

### Purpose
`test_cursor_bound14.py` validates write operations on bounded cursors. It checks that inserts, updates, reserves, modifies, and removes respect lower and/or upper bounds, including boundary inclusivity.

### Important APIs, Types, and Functions
The class derives from `bound_base` and expands scenarios over object types, key/value formats, cursor overwrite config, lower/upper/both bound selection, and eviction flags. It uses `cursor.insert`, `cursor.update`, `cursor.reserve`, `cursor.modify` with `wiredtiger.Modify`, `cursor.remove`, `wiredtiger.WT_NOTFOUND`, and error assertions for item-not-found messages.

### Control Flow and State
The test populates via `create_session_and_cursor`, inserts out-of-range keys 10 and 95, then sets selected bounds around 45-50. It attempts inserts outside the lower and upper bounds, expecting errors only for the active bound side. It updates existing out-of-bound records, reserves them inside a transaction, modifies string values when supported, and removes them, checking `WT_NOTFOUND` or success according to active bounds. It finally updates keys exactly at lower and upper boundaries, with results controlled by inclusive flags.

### Persistence and Integration
The test mutates persistent table state and uses transactions for reserve/modify cases. Column groups and composite values exercise bound checks through complex cursor implementations.

### Risks and Test Signals
Risks include write paths bypassing bounds, inconsistent error codes between insert and update-like operations, modify support leaking into unsupported value formats, and boundary inclusivity failures. Passing confirms bounds constrain both read and write APIs.
