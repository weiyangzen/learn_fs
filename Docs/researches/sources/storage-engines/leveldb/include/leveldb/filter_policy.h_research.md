# sources/storage-engines/leveldb/include/leveldb/filter_policy.h

Purpose: declares the filter-policy interface used to build per-table filters, usually bloom filters, to avoid unnecessary disk reads.

Important APIs and types: `FilterPolicy`, `Name`, `CreateFilter`, `KeyMayMatch`, and `NewBloomFilterPolicy`.

Control flow: table building calls `CreateFilter` with sorted user keys and appends the encoded filter to table metadata. Table reads call `KeyMayMatch` before reading data blocks for point lookups.

State and persistence behavior: filter bytes are persisted inside table files. `Name()` is a compatibility identifier and must change if encoding changes incompatibly.

Dependencies and integration: referenced from `Options::filter_policy` and internal table/filter block code. Custom comparators that ignore parts of keys require matching filter semantics.

Risks and edge cases: false positives are allowed, false negatives for existing keys are not. Using bytewise bloom filters with a comparator that ignores key suffixes can make existing keys unreachable.

Test signals: bloom/filter tests are elsewhere; this subset only covers integration through options/table APIs.
