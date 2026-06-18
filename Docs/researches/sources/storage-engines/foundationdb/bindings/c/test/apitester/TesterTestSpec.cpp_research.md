# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.cpp

## Purpose
Parses C API tester TOML files into `TestSpec` and `WorkloadSpec`, bridging declarative test scenarios and runtime tester options.

## Important APIs, types, and functions
`readTomlTestSpec` loads exactly one `[[test]]`, maps known keys through `testSpecTestKeys`, gathers optional `[[knobs]]`, and copies each `[[test.workload]]` table into a string option map. `processIntOption` enforces bounded ranges; `toml_to_string` normalizes TOML values for string-based workload configs.

## Control flow
The parser rejects missing/multiple test sections, rejects unknown test parameters, parses knobs if present, then requires every workload to include `name`.

## State and persistence behavior
No files or cluster state are written. The returned `TestSpec` is transient configuration later consumed by `fdb_c_api_tester.cpp`.

## Dependencies and integration points
Depends on `toml.hpp`, `fmt`, `TesterUtil::TesterError`, and `TesterTestSpec.h`. Its output drives network options, executor selection, randomization, and workload factory creation.

## Risks and test signals
Boolean parsing treats only `"true"` as true; malformed values can silently behave as false. Test signals are parser failures for invalid TOML and successful execution of all `apitester/tests/*.toml` scenarios.
