## sources/storage-engines/pebble/sstable/block_property_obsolete.go

Purpose: Implements a specialized block property that marks blocks/indexes/tables containing only obsolete keys so iterators can skip them.

Important APIs/types/functions: `obsoleteKeyBlockPropertyCollector`, `obsoleteKeyBlockPropertyFilter`, `AddPoint`, `obsoleteKeyBlockPropertyEncode`, and `obsoleteKeyBlockPropertyDecode`.

Control flow: The collector ignores generic `AddPointKey`/`AddRangeKeys`; obsolete-key-aware writer code calls the out-of-band `AddPoint(isObsolete)`. Finishing a data block encodes whether the block had no non-obsolete points and updates table state. `AddPrevDataBlockToIndexBlock` folds the just-finished block into index state and resets block state. `FinishIndexBlock` and `FinishTable` encode index/table obsolete-only state. The filter decodes the property and intersects only if the block may contain non-obsolete keys.

State and persistence behavior: Empty property means not obsolete; single byte `'t'` means obsolete-only. The collector tracks booleans for current block, current index block, and whole table. Suffix replacement validates old property but marks the block non-obsolete because rewriting loses obsolete certainty.

Dependencies and integration points: Depends on `BlockPropertyCollector`, `BlockPropertyFilter`, `base.AssertionFailedf`, and `errors`. Used with Pebble table format v4 obsolete-key semantics and table-cache filter insertion.

Risks: Because generic `AddPointKey` ignores keys, only callers that explicitly call `AddPoint` maintain correctness. Synthetic suffix intersection asserts if an obsolete block appears with suffix replacement, reflecting an invariant rather than graceful fallback. The filter is stateless by design for in-place slice modification elsewhere.

Test signals: Covered indirectly by block-property and table-format tests elsewhere; this subset does not include a direct obsolete-property test.
