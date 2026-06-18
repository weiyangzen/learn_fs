# sources/storage-engines/foundationdb/bindings/bindingtester/tests/test_util.py

## Purpose
`test_util.py` provides random data generation and stack-instruction helpers for bindingtester workloads. It centralizes generation of tuple-compatible values, random range/key-selector parameters, error tuple encoding, blocking commit instruction sequences, stack reordering, and length-prefixed argument lists.

## Important APIs, Types, And Functions
- `RandomGenerator` is configured by `max_int_bits`, `api_version`, and enabled type names.
- `random_int()`, `random_float()`, `random_tuple()`, `random_tuple_list()`, `random_range_params()`, `random_selector_params()`, `random_string()`, and `random_unicode_char()` generate edge-heavy data.
- `error_string(error_code)` encodes `(b"ERROR", b"<code>")` using `fdb.tuple.pack`.
- `blocking_commit(instructions)` emits `COMMIT`, `WAIT_FUTURE`, and `RESET`.
- `to_front(instructions, index)` recursively emits `SWAP` instructions to bring a stack entry to the front.
- `with_length(tup)` produces `(len(tup),) + tup` for stack-machine instructions that take counted argument lists.

## Control Flow
Random tuple generation selects enabled type names and recursively creates nested tuples, versionstamps, UUIDs, booleans with API-version compatibility, bytes, Unicode strings, and floats. Range/selectors bias toward common values while still sampling large limits and unusual offsets. Helper functions emit stack-machine operations but do not execute database calls directly.

## State And Persistence Behavior
This module has no persistent state. `RandomGenerator` holds only configuration; all data generation uses the process-global `random` module. Outputs become persistent only when caller workloads write generated keys/values to FoundationDB.

## Dependencies And Integration Points
It depends on `fdb`, `fdb.tuple`, `COMMON_TYPES`, Python `uuid`, `unicodedata`, `ctypes`, and `math`. It is used across bindingtester tests, especially tuple, directory, and scripted workloads.

## Risks And Edge Cases
Generated floats include NaN, infinities, negative zero, and wide exponent values, which can expose binding-specific encoding differences. Unicode generation includes multi-codepoint and private-use cases. `to_front()` emits multiple swaps recursively, so stack depth assumptions must match the interpreter. API-version handling for bool and versionstamp affects expected cross-version compatibility.

## Test Signals
The helper itself is not a test, but it creates high-value edge coverage for tuple encoding, range parameters, and stack behavior. `blocking_commit()` makes transaction boundaries explicit and repeatable in higher-level tests.
