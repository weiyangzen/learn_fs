# sources/storage-engines/sqlite/ext/misc/rot13.c

Purpose: registers a deterministic innocuous `rot13()` function and a `rot13` collation.

Important APIs/types/functions: byte helper `rot13()` transforms ASCII letters. `rot13func()` transforms one SQL value after UTF-8 text conversion. `rot13CollFunc()` compares two strings after bytewise rot13 mapping. `sqlite3_rot_init()` registers both.

Control flow: null input returns null. Short strings use a stack buffer, long strings allocate heap memory, transform bytes, return transient text, and free temporary storage. Collation transforms during comparison and falls back to length.

State and persistence: stateless after registration.

Dependencies/integration: SQLite scalar and collation APIs.

Risks/test signals: byte-oriented ASCII behavior, text conversion of non-text inputs, embedded nul/non-ASCII collation behavior, and allocation boundary. Test involution, nulls, mixed case, long input, non-ASCII preservation, and collation equivalence to transformed binary comparison.
