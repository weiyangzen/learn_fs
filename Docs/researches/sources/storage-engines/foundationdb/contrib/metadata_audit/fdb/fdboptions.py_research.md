# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/fdboptions.py

## Purpose
This generated-style module is the data table behind the local FDB Python binding. It defines numeric option, enum, mutation, and error-predicate constants plus documentation and parameter type metadata used by `impl.py` to create methods dynamically.

## Important APIs, Types, And Functions
The primary objects are dictionaries: `NetworkOption`, `DatabaseOption`, `TransactionOption`, `StreamingMode`, `MutationType`, `ConflictRangeType`, and `ErrorPredicate`. Each entry maps a symbolic name to `(code, description, parameter_type, parameter_description)`.

Notable options include TLS configuration, external client libraries, client threading, transaction timeouts/retry limits/size limits, system-key and lock-aware access, read priority, special key space writes, tracing tags, GRV cache, authorization token, and replica consistency check settings. `MutationType` includes arithmetic/bitwise atomics, byte min/max, compare-and-clear, and versionstamped key/value operations.

## Control Flow
There is no runtime control flow beyond module import. `impl.fill_options`, `impl.make_enum`, and `impl.fill_operations` iterate over these dictionaries to attach `set_*` methods to network/database/transaction option wrappers, expose streaming/conflict constants as properties, attach error predicate helpers, and add mutation helpers to `Database` and `Transaction`.

## State And Persistence Behavior
The module itself is stateless, but its constants control persistent and network-affecting behavior in the FDB C API. Several options directly enable system-key writes, lock awareness, transaction durability modes, timeouts, retries, tracing, TLS files, and mutation opcodes that alter database values at commit time.

## Dependencies And Integration Points
It is imported by `fdb.impl`. The `paramType` values must match the wrapper conversion logic in `option_wrap*`; a mismatch causes generated methods to pass incorrectly encoded C API parameters. The option codes must match the linked `libfdb_c` version.

## Risks And Edge Cases
Because this file is a hand/generated compatibility table, stale numeric codes are dangerous: wrong codes can silently set unrelated options or mutation types. Some keys include deprecated aliases, duplicate code values, or options gated by API version, so callers can see runtime C API errors despite method presence. System-key and lock-aware options are intentionally powerful and must not be exposed casually in high-level tools.

## Test Signals
Tests should import the binding, confirm expected methods are generated, verify parameter type validation for no-arg/string/bytes/int options, and exercise a small set of known C API options against a compatible client library. Static tests can compare codes with generated binding metadata from the same FDB version.
