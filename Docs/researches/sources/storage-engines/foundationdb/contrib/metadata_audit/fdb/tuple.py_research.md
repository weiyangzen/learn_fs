# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/tuple.py

## Purpose
This module implements FoundationDB tuple layer encoding for Python. It converts Python values into lexicographically ordered byte strings suitable for keys, decodes tuple keys, supports versionstamp packing, computes tuple subranges, and compares tuples using FDB tuple ordering.

## Important APIs, Types, And Functions
Public APIs are `pack`, `pack_with_versionstamp`, `unpack`, `has_incomplete_versionstamp`, `range`, and `compare`. Public value types are `SingleFloat` for 32-bit float encoding and `Versionstamp` for complete or incomplete transaction versionstamps.

Internal helpers include `_encode`, `_decode`, `_pack_maybe_with_versionstamp`, `_find_terminator`, `_float_adjust`, `_reduce_children`, `_code_for`, `_compare_floats`, and `_compare_values`. Type codes cover null, bytes, string, nested tuple/list, integers, floats/doubles, booleans, UUIDs, and versionstamps.

## Control Flow
Encoding dispatches by Python type. Bytes and strings escape embedded nulls and terminate with null. Integers encode around `INT_ZERO_CODE` with variable-width positive/negative encodings, including extended 9-255 byte forms. Floats flip sign bits or invert negative bytes to preserve numeric order. Nested tuples recursively encode children and use a special nested-null representation. Versionstamp packing tracks the single incomplete position and appends a little-endian offset of two bytes for old API versions or four bytes for newer versions.

Decoding reads one type code at a time from the byte stream and reconstructs values until the key ends. `range(t)` returns the slice between packed tuple plus `0x00` and packed tuple plus `0xff`, matching tuple-extension range semantics. `compare` uses tuple type code ordering and special float handling for negative zero, NaN, and infinities.

## State And Persistence Behavior
The module is stateless. Its encoded bytes define persistent key ordering for all higher-level code using tuple/subspace/directory abstractions. Versionstamp packing is intended for FDB atomic versionstamp mutations where the final offset bytes are interpreted at commit time.

## Dependencies And Integration Points
It depends on `ctypes`, `uuid`, `struct`, `math`, and the top-level `fdb` module for API-version behavior and `fdb.impl.Value` coercion in `Versionstamp.to_bytes`. `subspace_impl.py` and `directory_impl.py` rely on these encodings for all logical-to-physical key mapping.

## Risks And Edge Cases
Tuple encoding is compatibility-critical; any code-point or ordering change corrupts range scans and directory keys. Boolean handling changes with API version before 500. Only one incomplete versionstamp is allowed. Float comparison handles unusual values but can differ from Python's native NaN semantics. `_decode` raises on unknown type codes and can fail on malformed/truncated keys. The module shadows built-in `range` with tuple range after saving `_range`.

## Test Signals
Tests should include FDB tuple spec vectors, round trips for all supported types, ordering comparisons against packed byte order, nested tuples containing `None`, embedded null bytes, very large positive/negative integers, `SingleFloat`, NaN/negative-zero cases, UUIDs, complete and incomplete versionstamps, API-version gated boolean behavior, and prefix range boundaries.
