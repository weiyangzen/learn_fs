# sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.cpp

Purpose: Parses legacy text test specs and TOML test specs into `TestSpec`/`TestSet`, including workload options and scoped knob overrides.

Important APIs/types/functions: `testSpecGlobalKeys` accepts harness-level keys and side effects such as client info logging. `testSpecTestKeys` maps test-level attributes into `TestSpec` fields. `toml_to_string` normalizes TOML values. `readTests` parses legacy `key=value` text. `getOverriddenKnobKeyValues` parses TOML `knobs` arrays through client/server/flow knob parsers. `readTOMLTests_` parses `[[test]]`, nested workloads, and test-level knobs. `readTOMLTests` catches `std::exception` and converts to Flow `unknown_error`.

Control flow: Legacy parsing reads line by line, strips whitespace, routes recognized test/global keys, starts a new workload option group on `testName`, flushes option groups on new test titles, and returns specs with titles/options. TOML parsing reads global knobs, iterates tests, applies test-level fields, converts each `workload` table into a `VectorRef<KeyValueRef>`, then attaches per-test knobs.

State and persistence behavior: Produces in-memory `TestSpec` and `KnobKeyValuePairs`. It may set network options for client statistics logging. No file writes.

Dependencies and integration points: Uses `toml11`, Flow platform helpers, trace logging, native API types, knobs, `TestSpecParser.h`, and `KnobProtectiveGroups`. `runTests` calls it for `.txt` and `.toml` files.

Risks: Unknown legacy keys become workload options, so typos may only be caught later by option-consumption checks. TOML unknown test parameters log severe errors but parsing continues. Numeric parsing uses `sscanf`/asserts. TOML `workload` is required for each test via `toml::find`.

Test signals: Trace events `TestParserTest`, `TestParserOption`, `TestSpecUnrecognizedKnob`, `TestSpecUnrecognizedTestParam`, and `TOMLParseError`. Invalid specs surface later as `test_specification_invalid`.
