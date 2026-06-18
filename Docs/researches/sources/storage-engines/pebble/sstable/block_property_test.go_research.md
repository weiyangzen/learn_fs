## sources/storage-engines/pebble/sstable/block_property_test.go

Purpose: Comprehensive tests for block-property interval encoding, collection, filtering, writer/reader integration, bound-limited filters, and suffix replacement.

Important APIs/types/functions: Tests include `TestIntervalEncodeDecode`, `TestIntervalUnionIntersects`, `TestBlockIntervalCollector`, `TestBlockIntervalFilter`, `TestBlockPropertiesEncoderDecoder`, `TestBlockPropertiesFilterer_IntersectsUserPropsAndFinishInit`, `TestBlockPropertiesFilterer_Intersects`, `TestBlockProperties`, and `TestBlockProperties_BoundLimited`. Helpers include interval mappers, datadriven build/filter/iter runners, `boundLimitedWrapper`, `keyCountCollector`, and `testkeySuffixIntervalMapper`.

Control flow: Early unit tests validate interval and sparse property primitives. Filterer tests build table-level user properties, initialize short-ID maps, permute filter order, and check whole-table/per-block inclusion. Datadriven tests build real SSTables with selectable collectors, dump collector/table/block properties, evaluate table and block filters, and run point iterators. Bound-limited datadriven tests wrap filters to log `Intersects` and key-bound checks during iteration.

State and persistence behavior: Tests build real in-memory SSTables and inspect `Reader.UserProperties`, top-level and second-level index block handles with properties, and iterator-visible KVs. They exercise file-local short IDs and block/index/table property persistence.

Dependencies and integration points: Uses `datadriven`, `leaktest`, `base`, `keyspan`, `rangekey`, `testkeys`, `block`, SSTable `Reader`/`WriterOptions`, and iterator construction. It is a major integration test for block-property writer-reader behavior.

Risks: Some random collector tests use nondeterministic order/selection, though most behavior is datadriven. Helpers are powerful and can mask production-specific collectors not represented here. Value-based collector tests are useful but production value separation caveats remain.

Test signals: Very strong signal across serialization, filtering, table skipping, block skipping, two-level index decoding, synthetic suffix, and range-key masking interactions.
