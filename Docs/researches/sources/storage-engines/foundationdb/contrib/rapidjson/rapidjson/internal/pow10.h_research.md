# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/pow10.h

Purpose: This header supplies a fast lookup-table implementation for `10.0^n` used during decimal-to-double conversion.

Important APIs and functions: The single function is `internal::Pow10(int n)`, which asserts `0 <= n <= 308` and returns a `double` from a static table containing `1e0` through `1e308`.

Control flow: `Pow10()` performs only an assertion and direct array indexing. It avoids repeated multiplication or standard-library `pow()` calls for speed and predictable results.

State and persistence behavior: No mutable state or persistence. The static const table is read-only process data.

Dependencies and integration points: It depends on `rapidjson.h`. `strtod.h` uses it in `FastPath()` and normal-precision conversion when exponents fall in representable ranges.

Risks: The function only supports non-negative exponents up to the maximum finite decimal exponent for double. Callers must handle negative exponents by division and underflow ranges separately. Table correctness is fundamental to number parsing accuracy.

Test signals: Validate returned values for boundary exponents `0`, `1`, `22`, `308`, assert behavior for invalid exponents in debug builds, and cross-check representative values against standard conversion results in strtod tests.
