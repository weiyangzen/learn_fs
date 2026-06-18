# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030_data.rs

## Purpose
Provides the explicit GB18030-to-Unicode override table consumed by `gb18030.rs`. It captures private-use and standard-version mappings that should not rely solely on `encoding_rs`.

## Important APIs, Types, And Functions
Exports one constant: `GB18030_TO_UNICODE: &[(u32, char)]`. Entries encode one-, two-, or four-byte GB18030 byte sequences as big-endian `u32` keys paired with Unicode `char` values.

## Control Flow
There is no executable control flow. At runtime, `gb18030.rs` iterates this slice to build `DECODE_MAP` directly and `ENCODE_MAP` by converting each `u32` key to big-endian bytes and trimming leading zero bytes.

## State And Persistence
Static read-only data compiled into the binary. It is not persisted or mutated. Its order is not semantically important for hash-map lookups, but duplicate Unicode chars or duplicate keys would affect map construction.

## Dependencies And Integration Points
Only integrated by `codec/collation/encoding/gb18030.rs`. Tests in that module exercise representative table regions, including PUA ranges, two-byte `0xFE**` mappings, and four-byte mappings.

## Risks
The table is large and hand/generated data quality is the main risk. Duplicate keys or chars silently collapse when collected into hash maps. Incorrect mappings would produce cross-component incompatibility with TiDB/MySQL and make stored text compare or round-trip incorrectly.

## Test Signals
No local tests in the data file. Indirect tests in `gb18030.rs` assert encode/decode behavior for selected mappings from this table.
