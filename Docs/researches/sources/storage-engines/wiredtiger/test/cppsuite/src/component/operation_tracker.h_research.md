# sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.h

Purpose: Declares operation tracking schemas, operation enum, and the tracking component interface.

Important APIs/types/functions: macros define default row-operation and schema-operation key/value formats and schema table config. `tracking_operation` enumerates create, custom, delete collection, delete key, and insert. `operation_tracker` exposes table-name getters, lifecycle overrides, schema and row operation save APIs, and virtual `set_tracking_cursor` for custom schemas.

Control flow: callers attach the tracker to database/workload components, then saves happen during schema and data operations while the component sweeps in its own loop.

State and persistence: owns table names/configs, sessions/cursors, compression flag, and timestamp manager reference.

Dependencies/integration: inherits `component`, includes scoped storage wrappers and timestamp manager.

Risks and test signals: custom tracking formats disable default sweeping, which can grow tables. The virtual cursor setter is the extension point for non-default operation tracking, so overrides must match table format exactly.
