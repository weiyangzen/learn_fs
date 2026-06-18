# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/mod.rs

## Purpose
Defines the core collation and encoding contracts, compile-time dispatch macros, and `SortKey` wrapper used to compare/hash values according to SQL collation semantics.

## Important APIs, Types, And Functions
Macros: `match_template_collator!`, `match_template_multiple_collators!`, and `match_template_charset!`. Traits: `Charset`, `Collator`, and `Encoding`. `SortKey<T, C>` wraps byte-like data with a collator marker and implements `Hash`, `Eq`, `Ord`, `Clone`, and `Deref`.

## Control Flow
Template macros map enum-like tags to concrete collator/encoding types. `SortKey::new`, `new_ref`, and option mapping functions validate charset bytes before transmuting or wrapping. Ordering and equality call `C::sort_compare`; hashing calls `C::sort_hash`; owned sort-key bytes can be generated through `Collator::sort_key`.

## State And Persistence
`SortKey` stores only the original byte container and `PhantomData<C>`. It does not cache computed sort keys. Unsafe reference mapping relies on `repr(transparent)` and identical layout with the wrapped value.

## Dependencies And Integration Points
Integrates charset modules, collator implementations, encoding strategies, `codec::prelude::BufferWriter`, `num::Unsigned`, byte data types, and generated collation enums. It is the central API used by expression evaluation, comparison, hash aggregation, and sorting code.

## Risks
`new_unchecked` and unsafe transmute helpers can panic later if invalid bytes are compared or hashed. `Hash`/`Ord` unwrap collator results, so validation must happen before use. Macro mappings must stay synchronized with collation IDs.

## Test Signals
No local tests. Behavior is exercised through individual collators, charset validation, and SQL comparison tests.
