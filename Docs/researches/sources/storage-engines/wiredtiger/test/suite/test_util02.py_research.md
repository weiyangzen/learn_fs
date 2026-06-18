# sources/storage-engines/wiredtiger/test/suite/test_util02.py

## Purpose
`test_util02.py` tests `wt load` by dumping a populated table, loading it into a renamed table, and validating command-line metadata override handling.

## Important APIs, Types, and Functions
It defines `test_util02` with `get_string`, `get_key`, `get_value`, `dumpstr`, `table_config`, `load_process`, and load tests, plus `test_load_commandline` for command-line error/success combinations.

## Control Flow
The load-process tests create and populate a complex dataset, run `wt dump` optionally with `-x`, create a target table, run `wt load -f dump.out -r target`, and verify key/value formats and content. Command-line tests run `load` with varying trailing config arguments and check stderr presence/absence.

## State and Persistence Behavior
Dumped data is persisted through `dump.out` and reloaded into a second table. Metadata overrides are parsed but should reject invalid or duplicate configurations.

## Dependencies and Integration Points
Depends on `ComplexDataSet`, `suite_subprocess.runWt`, external `wt dump/load`, and scenario formats `SS`, `rS`, `ri`, and `ii`.

## Risks and Edge Cases
Command-line parsing is a major edge surface: invalid URI/config pairs must fail while allowed metadata keys are accepted.

## Test Signals
Reloaded cursor formats and values match originals; command-line cases produce expected empty or non-empty error files.
