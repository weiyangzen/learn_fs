# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/mod.rs

## Purpose
Implements Unicode Collation Algorithm based utf8mb4 collators for `utf8mb4_unicode_ci` and `utf8mb4_0900_ai_ci`. The file is a generic adapter over version-specific weight tables in `data_0400` and `data_0900`.

## Important APIs, Types, And Functions
`CollatorUtf8Mb4UnicodeCi` and `CollatorUtf8Mb40900AiCi` are type aliases over `CollatorUca<T>`. `UnicodeVersion` supplies `preprocess` and `char_weight`. `CollatorUca<T>` implements `Collator` with UTF-8 charset, `u128` weights, and case-insensitive semantics. The key methods are `write_sort_key`, `sort_compare`, and `sort_hash`.

## Control Flow
Each operation first applies version-specific preprocessing unless `sort_compare` is forced to no-pad. It then streams valid UTF-8 characters through `next_utf8_char`, obtains a packed `u128` collation weight, and processes 16-bit weight units from low to high. Sort-key writing serializes those units big-endian. Comparison lazily expands weights for both inputs, skips zero weights, and compares the first differing 16-bit unit. Invalid/truncated UTF-8 stops iteration and returns equality or the partial key/hash result.

## State And Persistence
The collator is stateless. `PhantomData<T>` binds the selected Unicode version at the type level. Persistent behavior is delegated to static data tables in the sibling modules.

## Dependencies And Integration Points
Depends on the parent collator framework, `CharsetUtf8mb4`, `BufferWriter`, `Hasher`, `Ordering`, and `next_utf8_char`. It is selected through the collation macros in `codec/collation/mod.rs`.

## Risks
Packed-weight ordering depends on the low-to-high 16-bit unpacking convention matching the generated tables. Invalid UTF-8 handling is permissive and can treat malformed tails as equal. Preprocessing controls padding behavior, so version-specific mistakes affect equality, hashing, and ordering together.

## Test Signals
No tests are local to this file. Coverage is expected through collation integration tests and generated data-table tests elsewhere.
