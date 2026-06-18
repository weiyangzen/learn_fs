# sources/test-tools/crashmonkey/code/results/DataTestResult.cpp

Purpose: implements user-data consistency error tracking and formatting.

Important APIs/functions: constructor and `ResetError()` set the state to `kClean`; `SetError()` assigns the given error; `GetError()` returns it; `PrintErrors()` iterates bit flags; `operator<<` maps enum values to stable text tokens.

Control flow and state: test cases call `SetError()` and optionally fill `error_description`; `SingleTestInfo` later prints the data errors and uses them for result classification.

Dependencies: paired with `DataTestResult.h`, used by `BaseTestCase` implementations and `TestSuiteResult`.

Risks: `SetError()` overwrites rather than ORs, unlike `FileSystemTestResult`, so multiple data errors cannot be accumulated. `PrintErrors()` prints adjacent tokens without separators. Namespace-local bit constants in the header can create independent internal-linkage constants per translation unit, though they are compile-time values.

Test signals: unit tests should assert text output for every enum and behavior when setting multiple errors sequentially.
