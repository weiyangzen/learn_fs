# sources/storage-engines/tikv/components/engine_panic/src/compact.rs

Purpose: Panic stubs for compaction control and compaction-event reporting.

Important APIs and types: `PanicEngine` implements `CompactExt`; `PanicCompactedEvent` implements `CompactedEvent` with key-range, declined-byte, output-level, region decline calculation, and CF accessors.

Control flow and state: All compaction operations and event accessors panic. No compaction state exists.

Dependencies and integration: Mirrors real engine APIs for manual compaction, file compaction, range validation, and split-check event consumption.

Risks: Runtime invocation panics. Trait drift here would reveal missing methods during compile.

Test signals: No tests.
