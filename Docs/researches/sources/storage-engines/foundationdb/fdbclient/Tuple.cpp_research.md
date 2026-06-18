# sources/storage-engines/foundationdb/fdbclient/Tuple.cpp

## Purpose
`Tuple.cpp` implements FoundationDB tuple packing and unpacking for ordered key encoding. It supports byte strings, UTF-8 strings, signed integers, floats, doubles, booleans, null, 96-bit versionstamps, and restricted user-defined terminal types.

## Important APIs, types, and functions
Constants include `VERSIONSTAMP_96_CODE`, `USER_TYPE_START`, and `USER_TYPE_END`. Helpers `bigEndianFloat()`, `bigEndianDouble()`, `findStringTerminator()`, and `adjustFloatingPoint()` implement sortable encodings. Constructors parse packed data and populate element offsets. Public methods include `unpack()`, `unpackUserType()`, `tupleToString()`, append overloads, `getType()`, typed getters, `range()`, `subTuple()`, and `subTupleRawString()`.

## Control flow
Parsing walks the packed byte string, records each element offset, and advances according to the type code. Byte and UTF-8 strings terminate on `0x00` not followed by escaped `0xff`; integers use type-code-relative byte lengths around `0x14`; floats and doubles have fixed lengths; versionstamps have `VERSIONSTAMP_TUPLE_SIZE`; user types are allowed only when explicitly requested and consume the remaining bytes. Append methods write canonical ordered encodings: strings escape embedded NULs as `00 ff`, integers use minimal big-endian sign-aware lengths, floating point values are endian-swapped then sign-adjusted for lexical order, and null/bool/versionstamp/user types write fixed codes. Getters validate index and type before decoding.

## State and persistence behavior
`Tuple` stores packed bytes and offsets in arena-backed vectors. It does not write the database directly, but packed tuple bytes are widely persisted as keys and subspace suffixes. Encoding changes are therefore persistent format changes.

## Dependencies and integration points
It depends on `Tuple.h`, `TupleVersionstamp`, Flow unit tests, endian helpers, arenas, `KeyRange`, and FoundationDB error types. `Subspace`, `TaskBucket`, and many system key helpers use tuple packing.

## Risks and edge cases
Tuple parsing throws on unknown data types, and user-defined types are rejected unless `unpackUserType()` is used. `exclude_incomplete` can drop incomplete trailing elements, while `getInt(..., allow_incomplete)` has special sort-preserving behavior for truncated integers. Floating-point encoding depends on bit reinterpretation and endian conversion. `getString()` reconstructs escaped strings into a new arena; callers should not expect zero-copy. `range()` uses appended `0x00`/`0xff` bounds and should be used consistently with tuple prefix semantics.

## Test signals
Local tests cover `makeTuple()` equivalence with append chains and `unpackUserType()` behavior, including rejection by normal unpack. Additional coverage should include integer ordering across negative/zero/positive boundaries, embedded NUL strings, float/double ordering including negative values, incomplete tuple parsing, subtuple extraction, range bounds, and versionstamp round trips.
