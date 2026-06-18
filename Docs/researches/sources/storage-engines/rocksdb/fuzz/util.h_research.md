<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/util.h -->
# sources/storage-engines/rocksdb/fuzz/util.h

## Purpose

`fuzz/util.h` provides small abort-on-failure assertion macros used by RocksDB fuzz harnesses. They keep harness code compact while converting semantic mismatches or bad statuses into fuzzer-detectable crashes.

## Important APIs, Types, and Functions

- `CHECK_OK(expression)` evaluates a RocksDB-style status expression, prints `ToString()` on failure, and aborts.
- `CHECK_EQ(a, b)` compares two expressions with `!=`, prints both expression names and values, and aborts on mismatch.
- `CHECK_TRUE(cond)` aborts when a condition is false.

## Control Flow

Each macro is inline preprocessor control flow. `CHECK_OK` uses a `do { ... } while (0)` wrapper and stores the evaluated status once. `CHECK_EQ` and `CHECK_TRUE` expand to simple `if` statements that print to `std::cerr` then abort.

## State and Persistence Behavior

The macros have no persistent state. Their side effects are diagnostic writes to stderr and process aborts, which libFuzzer treats as findings.

## Dependencies and Integration Points

They assume included code has access to `std::cerr`, `std::endl`, and `abort()`, and that status objects expose `ok()` and `ToString()`. They are used by proto fuzzers such as `db_map_fuzzer.cc` and `sst_file_writer_fuzzer.cc`.

## Risks and Edge Cases

`CHECK_EQ` evaluates `a` and `b` more than once when the comparison fails because it also prints them, so arguments should be side-effect-free. The macros are intentionally fatal and unsuitable for tests that need cleanup or multiple failure aggregation. Missing includes are tolerated only because current users include iostream/cstdlib indirectly or directly.

## Test Signals

Signals are straightforward: bad statuses and mismatches abort with useful diagnostics, while success paths add minimal overhead. Harness review should ensure macro arguments are side-effect-free.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/fuzz/util.h -->
