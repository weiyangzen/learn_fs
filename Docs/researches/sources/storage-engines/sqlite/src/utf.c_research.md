# sources/storage-engines/sqlite/src/utf.c

## Purpose
`utf.c` provides SQLite's internal Unicode text encoding primitives. It reads and writes UTF-8 code points, converts VDBE `Mem` strings among UTF-8, UTF-16LE, and UTF-16BE, handles UTF-16 byte-order marks, counts UTF-8/UTF-16 characters or byte lengths, and exposes debug/test helpers for UTF validation. These routines sit underneath SQL text values, API calls, collations, scalar functions, and database encodings.

## Important APIs, Types, And Functions
Important macros are `WRITE_UTF8`, `WRITE_UTF16LE`, `WRITE_UTF16BE`, and `READ_UTF8`. The first-byte lookup table `sqlite3Utf8Trans1[]` accelerates UTF-8 decoding. Public functions include `sqlite3AppendOneUtf8Character()`, `sqlite3Utf8Read()`, `sqlite3Utf8ReadLimited()`, `sqlite3VdbeMemTranslate()`, `sqlite3VdbeMemHandleBom()`, `sqlite3Utf8CharLen()`, `sqlite3Utf8To8()` in debug test builds, `sqlite3Utf16to8()`, `sqlite3Utf16ByteLen()`, and `sqlite3UtfSelfTest()` in test builds. Key data types are `Mem`, `sqlite3`, `u8`, `u32`, and VDBE memory flags such as `MEM_Str`, `MEM_Term`, subtype, affinity, and allocation ownership bits.

## Control Flow
UTF-8 decode starts with a single byte. For multibyte sequences, `sqlite3Utf8Read()` and `READ_UTF8` fold continuation bytes into a code point and replace NUL overlongs, surrogate encodings, and U+FFFE/U+FFFF with U+FFFD. `sqlite3Utf8ReadLimited()` is a bounded variant used when input is not zero-terminated; it reads at most four bytes and does less validation.

`sqlite3VdbeMemTranslate()` is the main conversion path. UTF-16-to-UTF-16 conversion is an in-place byte swap after making the `Mem` writeable. UTF-8-to-UTF-16 allocates a worst-case output buffer and emits little- or big-endian units. UTF-16-to-UTF-8 reads 16-bit units, combines surrogate pairs, optionally replaces invalid surrogates under `SQLITE_REPLACE_INVALID_UTF`, writes UTF-8 bytes, terminates the buffer, releases the old `Mem` payload, and installs the new allocation with updated flags and encoding.

`sqlite3VdbeMemHandleBom()` detects UTF-16 BOMs, makes the memory writeable, removes the first two bytes, terminates the string, and updates `Mem.enc`. `sqlite3Utf16to8()` wraps a transient `Mem` around API input and asks VDBE memory code to convert it. Character-count helpers advance by encoded characters rather than bytes.

## State And Persistence Behavior
The routines mutate transient in-memory values, not database pages directly. `sqlite3VdbeMemTranslate()` can allocate a new buffer, release the old representation, update `pMem->z`, `zMalloc`, `szMalloc`, `n`, `enc`, and flags, and preserve affinity/subtype bits. BOM handling removes bytes in place. These conversions affect persistent behavior indirectly because values are compared, stored, serialized, and returned through the encoding selected by the database and API.

Invalid UTF handling is intentionally SQLite-specific: overlong encodings for values >= 0x80 are accepted, overlong NULs and surrogate/noncharacters are replaced, and standalone continuation bytes are treated as single-byte values by `sqlite3Utf8Read()`. Those choices are externally visible in functions, collations, and APIs.

## Dependencies And Integration Points
`utf.c` depends on `sqliteInt.h` and `vdbeInt.h`, especially `Mem` ownership and allocation helpers from VDBE memory code. It integrates with `vdbemem.c` through `sqlite3VdbeChangeEncoding()`, SQL functions such as `length()`/`substr()`, collation and comparison paths, UTF-16 public APIs (`sqlite3_open16`, `sqlite3_column_text16`, `sqlite3_complete16`), tokenizer/parser input conversion, and test harness support. Compile-time gates include `SQLITE_OMIT_UTF16`, `SQLITE_TEST`, `SQLITE_DEBUG`, byte-order configuration, and `SQLITE_REPLACE_INVALID_UTF`.

## Risks And Edge Cases
Risks concentrate around buffer sizing, termination, odd UTF-16 byte counts, surrogate-pair handling, and preserving `Mem` ownership flags. UTF-16 input length is forced even in some paths; BOM removal must leave a two-byte terminator. Invalid UTF behavior is compatibility-sensitive and cannot simply be replaced with strict Unicode rules. `sqlite3Utf16to8()` returns the owned `Mem` buffer to the caller, so callers must free it with SQLite allocation discipline. In-place UTF-16 endian swapping requires a writeable buffer and correct `pMem->n` masking.

## Test Signals
Relevant tests include `enc*.test`, `utf16align.test`, `func.test` UTF length cases, `func3.test` encoding-specific function registration, `capi3e.test`, `mutex2.test`, `types.test`, and TCL tests using `sqlite3_column_text16`, `sqlite3_open16`, or `sqlite3_complete16`. Useful low-level signals are `translate_selftest` in test builds, malformed UTF sequences, BOM-prefixed strings, odd byte counts, surrogate pairs, invalid surrogates, UTF-16BE/LE round trips, and memory-fault injection in conversion paths.
