# sources/test-tools/crashmonkey/code/results/DataTestResult.h

Purpose: declares `DataTestResult`, the data-consistency result object used by test cases.

Important APIs/types: `ErrorType` includes clean, old file persisted, file missing, data corrupted, metadata corrupted, incorrect block count, other, and automated-check failure bits. Public fields/methods include `ResetError()`, `SetError()`, `GetError()`, `PrintErrors()`, and `error_description`.

Control flow and integration: `BaseTestCase::check_test()` implementations receive a pointer and set errors; `SingleTestInfo` embeds one; `TestSuiteResult` tallies it.

State: private `error_summary_` plus public description string. State is not persisted except through log output.

Risks: the enum is bitmask-shaped but API and tallying mostly treat it as a single value. Header-level anonymous namespaces are unusual in headers and create per-translation-unit constants.

Test signals: compile/link tests across multiple translation units and tally tests for each error type.
