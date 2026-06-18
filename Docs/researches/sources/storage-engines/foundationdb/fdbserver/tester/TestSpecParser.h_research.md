# sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.h

Purpose: Declares parser outputs and entry points for tester spec files.

Important APIs/types/functions: `TestSet` groups global `KnobKeyValuePairs overrideKnobs` with `std::vector<TestSpec> testSpecs`. Declares `readTests(std::ifstream&)` for legacy text and `readTOMLTests(std::string)` for TOML.

Control flow: Header only; parsing flow is in `TestSpecParser.cpp`.

State and persistence behavior: `TestSet` carries in-memory parsed configuration and knob overrides. No durable state.

Dependencies and integration points: Includes `WorkloadUtils.h` for `TestSpec` and `KnobKeyValuePairs`. Used by `test.cpp` to materialize test runs from file names.

Risks: Header couples parser users to workload utilities and knob protective types. API returns full vectors by value, which is appropriate for parsed spec ownership.

Test signals: Compile/link coverage and parser trace events in implementation.
