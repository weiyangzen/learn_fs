# sources/storage-engines/wiredtiger/test/suite/test_turtle01.py

## Purpose
`test_turtle01.py` validates the `WiredTiger.turtle` metadata file for both empty and non-empty databases, especially the stored version fields and checkpoint metadata formatting.

## Important APIs, Types, and Functions
The class defines constants for turtle keys and regex formats, plus `init_values`, `test_validate_turtle_file`, `check_metadata`, `find_and_check_wt_version`, `check_turtle`, `find_kv`, and `read_turtle`.

## Control Flow
The test reads the initial turtle file and validates version fields. It then creates `table:test_turtle`, writes 1,000 rows in one transaction, checkpoints, rereads the turtle file, revalidates version fields, and checks that checkpoint metadata in the final line is comma-separated.

## State and Persistence Behavior
The file directly reads persisted `WiredTiger.turtle`. Table creation and checkpointing should update metadata while preserving consistent version key/value pairs.

## Dependencies and Integration Points
Depends on `wttest`, Python `re`, WiredTiger's metadata/turtle file layout, and the local filesystem.

## Risks and Edge Cases
Regex strings use non-raw `\d` escapes, which work today but produce Python syntax warnings. The test assumes turtle file key/value lines and final metadata layout.

## Test Signals
Signals are successful regex matches, equality between numeric version tuple and version-string tuple, and comma-separated checkpoint metadata.
