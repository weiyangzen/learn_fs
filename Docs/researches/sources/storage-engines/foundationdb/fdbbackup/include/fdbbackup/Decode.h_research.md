# sources/storage-engines/foundationdb/fdbbackup/include/fdbbackup/Decode.h

## Purpose

`Decode.h` is a small public header for backup CLI string decoding. It declares the function used by `backup.cpp` to transform user-supplied hex-escaped restore prefixes into byte strings.

## Important APIs, Types, and Functions

The only API is `std::string decode_hex_string(std::string line, bool& err)`. The input is passed by value, allowing the implementation to modify a copy if needed. `err` is an out-parameter indicating parse failure, instead of throwing. The return value is the decoded byte string.

## Control Flow

The header itself has no control flow beyond include guards and `#pragma once`. Its observable behavior is through callers. In `backup.cpp`, `decode_hex_string` is called for `--add-prefix` and `--remove-prefix`; if `err` is set, the CLI prints a targeted parse error and exits before submitting a restore.

## State and Persistence Behavior

The header defines no persistent state. Its output can affect persistent restore behavior because decoded prefixes are passed into `FileBackupAgent::restore`, determining how restored keys are transformed in the destination database.

## Dependencies and Integration Points

It depends only on `<string>`. It is included by `fdbbackup/backup.cpp` and is part of the `fdbbackup` include surface rather than a local anonymous helper. The parser complements `backup.cpp` key-range parsing, which handles quoted strings and `\xNN` escapes for range arguments.

## Risks and Edge Cases

Because error reporting uses a mutable boolean out-parameter, callers must initialize or check it correctly. Prefix decoding is security-sensitive in restore workflows: a misdecoded prefix can restore into the wrong keyspace, especially system-key prefixes used by validation tests. There is no namespace, so the function name is global.

## Test Signals

The BulkDump/BulkLoad validation script passes `--add-prefix '\xff\x02/rlog/'`, exercising this API through `fdbrestore`. Restore-prefix failures would break audit-based restore validation and any tests using prefixed restore into system keyspace.
