# sources/storage-engines/sqlite/ext/misc/shathree.c

Purpose: registers SHA-3 scalar, aggregate, and query hash helpers for 224/256/384/512-bit variants.

Important APIs/types/functions: `SHA3Context` stores Keccak state, rate, byte-order mask, and size. `KeccakF1600Step()`, `SHA3Init()`, `SHA3Update()`, and `SHA3Final()` implement SHA-3. SQL callbacks are `sha3Func()`, `sha3AggStep()`, `sha3AggFinal()`, `sha3QueryFunc()`, and `sha3UpdateFromValue()`.

Control flow: scalar calls validate size and hash blob bytes or UTF-8 text. Aggregate calls hash every input, including nulls, using type tags. Query calls prepare read-only statements, hash SQL text and type-tagged result rows, and reject writes.

State and persistence: scalar/query state is local; aggregate state lives in SQLite aggregate context. No database writes.

Dependencies/integration: SQLite function/aggregate APIs, direct-only query registration, and endian-aware Keccak implementation.

Risks/test signals: invalid size handling, aggregate ordering dependence, endian optimized path, and arbitrary read-only query execution. Test NIST vectors, all sizes, blob/text equivalences, aggregate with `ORDER BY`, null/type encodings, query write rejection, and endian portability.
