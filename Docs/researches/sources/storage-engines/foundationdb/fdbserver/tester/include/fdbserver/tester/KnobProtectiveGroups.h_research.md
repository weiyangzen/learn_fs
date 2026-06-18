# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/KnobProtectiveGroups.h

Purpose: Declares RAII types for collecting and applying temporary knob overrides in tester runs.

Important APIs/types/functions: `KnobKeyValuePairs` owns an `unordered_map<std::string, ParsedKnobValue>` and provides `set`/`getKnobs`. `KnobProtectiveGroup` stores original and overridden knob sets and declares constructor, destructor, `snapshotOriginalKnobs`, and `assignKnobs`.

Control flow: Header expresses the RAII contract: constructing a protective group applies overrides; destroying it restores originals.

State and persistence behavior: Holds knob values in memory and indirectly mutates global knob state through implementation.

Dependencies and integration points: Includes `flow/Knobs.h` for `ParsedKnobValue`. Used by TOML parser and main test orchestrator to apply global/per-test knobs.

Risks: Header exposes mutable global side effects through an apparently small utility. Copy/move behavior is not explicitly disabled for `KnobProtectiveGroup`, so usage should remain via `unique_ptr`/stack non-copy patterns.

Test signals: Compile coverage plus implementation trace events. TOML knob override tests exercise the declarations.
