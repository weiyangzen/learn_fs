# sources/storage-engines/tikv/components/engine_panic/src/table_properties.rs

Purpose: Minimal panic/empty skeleton for table properties.

Important APIs and types: `UserCollectedProperties` returns `None` for property lookups, approximate size/keys, and MVCC properties. `TableProperties` panics for user-collected properties and number of entries. `TablePropertiesCollection::iter_table_properties` is a no-op. `PanicEngine` implements `TablePropertiesExt`.

Control flow and state: Collection iteration silently does nothing, while engine lookup and table accessors panic. No table-property state is stored.

Dependencies and integration: Mirrors the property APIs used for range statistics, MVCC statistics, and table inspection.

Risks: The no-op collection may hide invocation compared with other panic stubs, but `table_properties_collection` itself panics before a collection can be obtained.

Test signals: No tests.
