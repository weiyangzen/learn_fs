# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Atomic.h

Purpose: inline implementations for FoundationDB atomic mutation semantics and versionstamp transformation.

Important APIs and functions: provides `doLittleEndianAdd`, bitwise `doAnd/Or/Xor`, `doAndV2`, `doAppendIfFits`, integer-style `doMax/Min`, bytewise `doByteMax/ByteMin`, `doMinV2`, `doCompareAndClear`, `placeVersionstamp`, `parseVersionstampOffset`, `getVersionstampKeyRange`, `transformVersionstampKey`, and `transformVersionstampMutation`.

Control flow: atomic helpers treat absent values as empty or as special V2 behavior, allocate results in an `Arena`, and preserve operand-size semantics. Versionstamp helpers read a little-endian 4-byte offset suffix, validate room for the 10-byte versionstamp, write big-endian version and transaction number, and convert versionstamped mutations to `SetValue`.

State and persistence: no global state, but returned `ValueRef`s point into caller-provided arenas or existing operands. Versionstamp transformation mutates string buffers in place and changes mutation type, affecting committed key/value bytes.

Dependencies and integration: included by write-map/read-your-writes and commit paths. Depends on `CommitTransaction.h`, mutation types, client knobs such as `VALUE_SIZE_LIMIT`, endian helpers, and FDB error codes.

Risks: arena lifetime must outlive returned refs. Empty operand semantics are subtle and differ across operations. Versionstamp offset validation is security-critical; invalid offsets throw `client_invalid_operation`.

Test signals: atomic mutation correctness tests and read-your-writes coalescing tests; `AppendIfFits` emits a code probe when truncation preserves existing value.
