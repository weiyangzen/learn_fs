# sources/storage-engines/wiredtiger/test/suite/test_util09.py

## Purpose
`test_util09.py` tests `wt loadtext` from a file and stdin, for both empty input and populated text input.

## Important APIs, Types, and Functions
The class defines `populate_file`, `check_keys`, and four test methods. It uses `runWt(['loadtext', ...])`, `infilename`, a string table, and cursor scans.

## Control Flow
Each test creates `table:test_util09.a`, writes `loadtext.in` with either no key/value pairs or a numeric range, runs `wt loadtext` using `-f` or stdin, and scans the table to verify loaded keys and values.

## State and Persistence Behavior
The loaded text creates persistent string-key/string-value table entries. Empty input must leave the table empty; populated input must create exactly the generated pairs.

## Dependencies and Integration Points
Depends on external `wt loadtext`, filesystem input file handling, stdin redirection through `suite_subprocess`, and cursor validation.

## Risks and Edge Cases
Input pair formatting and range boundaries are the main risks. Separate stdin/file modes protect two command paths.

## Test Signals
`check_keys` verifies every expected key maps to its generated value and that no extra keys are present.
