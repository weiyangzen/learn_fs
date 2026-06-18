# sources/storage-engines/rocksdb/db/wide/wide_columns.cc

Purpose: This file defines the global default wide-column name, an empty wide-column vector, and the non-inline `PinnableWideColumns::CreateIndexForWideColumns()` implementation that interprets pinned serialized wide-column bytes.

Important APIs/types/functions: It defines `kDefaultWideColumnName` as the empty `Slice`, `kNoWideColumns` as an empty `WideColumns`, and `PinnableWideColumns::CreateIndexForWideColumns()`. The function populates `columns_` and `unresolved_blob_column_indices_` from the currently pinned `value_`.

Control flow: `CreateIndexForWideColumns()` clears any previous index, attempts V1/generic `WideColumnSerialization::Deserialize`, and returns its status unless it is `NotSupported`. A `NotSupported` status can mean V2 bytes contain blob references after partially filling `columns_`; the method clears the partial result, resets the input slice, calls `DeserializeV2`, and records only the indexes of blob-backed columns in `unresolved_blob_column_indices_`.

State and persistence behavior: `PinnableWideColumns` keeps the serialized bytes in `value_` and builds column slices pointing into that storage. The unresolved blob index vector is transient state identifying which column values still require blob fetching; it does not resolve or persist blob contents. Clearing partial V1 results before V2 fallback prevents stale or mixed indexing state.

Dependencies and integration points: The file depends on `rocksdb/wide_columns.h`, `db/blob/blob_index.h`, and `db/wide/wide_column_serialization.h`. It integrates read paths that return `PinnableWideColumns`, V2 serialization with blob references, and callers checking `has_unresolved_blob_columns()`.

Risks: Correctness depends on V1 `Deserialize` returning `NotSupported` for V2 blob references and on `DeserializeV2` requiring an empty output vector. Any new V2 unsupported condition must be distinguished from blob-reference fallback. Slices in `columns_` remain valid only while `value_` backing storage remains valid.

Test signals: `wide_column_serialization_test.cc` directly tests fallback through `PinnableWideColumnsFallbacksToV2` and blob-reference rejection via generic deserialize/default-column APIs.
