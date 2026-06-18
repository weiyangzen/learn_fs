# sources/storage-engines/sqlite/ext/misc/ieee754.c

Purpose: registers SQL functions for exact inspection and construction of IEEE-754 binary64 values, including mantissa/exponent, blob, integer-bit, and ULP-style increment helpers.

Important APIs/types/functions: `ieee754func()` backs `ieee754()`, `ieee754_mantissa()`, and `ieee754_exponent()` via `sqlite3_user_data()`. `ieee754func_to_blob()`, `ieee754func_from_blob()`, `ieee754func_to_int()`, `ieee754func_from_int()`, and `ieee754inc()` expose raw representations. `sqlite3_ieee_init()` registers all functions.

Control flow: one-argument calls decode either an 8-byte big-endian blob or a numeric value, normalize sign/mantissa/exponent, and return a component or `ieee754(m,e)` text. Two-argument calls clamp exponent inputs, normalize mantissa width, assemble binary64 fields, and return a double.

State and persistence: stateless after function registration.

Dependencies/integration: SQLite scalar function API, `memcpy()` bit copying, and binary64 layout assumptions. Pairs with the decimal extension for exact decimal display.

Risks/test signals: negative zero, subnormals, infinities/NaNs, exponent clipping, and raw-bit increment semantics. Test blob/int round trips, max/min/subnormal values, zero variants, and reconstruction from mantissa/exponent.
