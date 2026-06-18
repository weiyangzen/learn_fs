# sources/storage-engines/foundationdb/fdbserver/tester/KnobProtectiveGroups.cpp

Purpose: Implements scoped knob overrides for tests, restoring original knob values when the scope ends.

Important APIs/types/functions: `KnobKeyValuePairs::set` inserts unique parsed knob values. `getKnobs` exposes the map. `KnobProtectiveGroup` constructor snapshots current values and assigns overrides. Destructor restores originals. `snapshotOriginalKnobs` searches client, server, then flow knobs. `assignKnobs` converts parsed values to `KnobValueRef` and calls `trySetServerKnob`.

Control flow: Construction snapshots every knob named in the override set, then applies override values. Destruction applies the saved original set. Missing knobs assert. Assignment traces and asserts on failure.

State and persistence behavior: Mutates process-global knob state for the lifetime of the protective group. Original values are held in memory only and restored by RAII.

Dependencies and integration points: Depends on `flow/Knobs.h`, `fdbclient/Knobs.h`, `fdbserver/core/Knobs.h`, parsed knob variants, and trace logging. Used by `TestSpecParser` and `test.cpp` for global and per-test TOML knob overrides.

Risks: Duplicate knob names assert in `set`. RAII restoration depends on destructor execution; process aborts skip restoration. `trySetServerKnob` is used for all knob categories after resolving values, so cross-category behavior depends on that helper recognizing the name.

Test signals: Trace events `SnapshotKnobValue`, `AssignKnobValue`, and `FailedToAssignKnob`. TOML tests with `[knobs]` exercise the path.
