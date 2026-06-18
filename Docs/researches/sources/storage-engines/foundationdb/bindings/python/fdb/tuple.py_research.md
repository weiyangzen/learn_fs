# sources/storage-engines/foundationdb/bindings/python/fdb/tuple.py

Purpose: This module implements FoundationDB tuple layer encoding for Python. It turns typed tuples into byte strings whose lexicographic order matches tuple order and decodes those byte strings back into Python values.

Important APIs and types: Public APIs are `pack`, `pack_with_versionstamp`, `unpack`, `range`, `compare`, `has_incomplete_versionstamp`, `SingleFloat`, `Versionstamp`, and `int2byte`. Supported encoded types include `None`, `bytes`, UTF-8 `str`, signed integers, single and double floats, booleans, UUIDs, nested tuples/lists, and versionstamps.

Control flow: `_encode` dispatches by Python type, assigns FoundationDB tuple type codes, escapes embedded null bytes, encodes integers with length-sensitive positive/negative forms, adjusts float sign bits for sortability, and tracks incomplete versionstamp position. `_pack_maybe_with_versionstamp` appends the little-endian versionstamp position when needed. `_decode` reverses each type-code encoding. `compare` mirrors tuple ordering without packing.

State and persistence behavior: The module is stateless apart from constants. Its byte output is persistent key format, so changes are compatibility-sensitive. Versionstamp packing differs for API versions before 520 versus newer APIs, and boolean treatment is API-version-aware.

Dependencies and integration points: It depends on `ctypes`, `uuid`, `struct`, `math`, `bisect`, and `fdb` version state. `Subspace`, directory layers, binding testers, and user schemas rely on its ordering and binary stability.

Risks: Edge cases include NaN ordering, negative zero, large integer bounds, nested `None` terminator escaping, API-version-specific boolean/versionstamp behavior, and incomplete versionstamp multiplicity. A bug changes persistent key order and can corrupt higher-level abstractions.

Test signals: `tuple_tests.py` performs randomized pack/unpack/order/range checks over bytes, strings, large integers, floats, booleans, UUIDs, and nested values. `tester.py` also exercises tuple packing, sorting, ranges, float encode/decode, and versionstamp packing behavior.
