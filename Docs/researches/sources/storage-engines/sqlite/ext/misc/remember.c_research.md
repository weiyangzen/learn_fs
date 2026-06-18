# sources/storage-engines/sqlite/ext/misc/remember.c

Purpose: registers `remember(value, ptr)`, a pass-through integer function that also writes the value through a bound C pointer.

Important APIs/types/functions: `rememberFunc()` reads `argv[0]` as `sqlite3_int64`, obtains `sqlite3_value_pointer(argv[1], "carray")`, stores through the pointer if present, and returns the integer. `sqlite3_remember_init()` registers the function.

Control flow: every call returns the integer input; side effect is conditional on a valid pointer with matching type tag.

State and persistence: only caller-owned memory pointed to by the bound pointer is modified; no database state is written by the function itself.

Dependencies/integration: SQLite pointer binding APIs and the `"carray"` pointer type convention shared with carray.

Risks/test signals: unsafe for untrusted SQL with pointer access; caller owns lifetime/alignment/type correctness. Test valid pointer writes, wrong/null pointer tags, use in an update statement, and integer conversion behavior.
