# sources/storage-engines/sqlite/ext/misc/decimal.c

## Purpose

`decimal.c` implements arbitrary-precision decimal math functions, a `decimal_sum` window aggregate, and a `decimal` collation. The implementation favors exactness and simplicity over speed.

## Important APIs, types, and functions

`sqlite3_decimal_init()` registers scalar functions `decimal`, `decimal_exp`, `decimal_cmp`, `decimal_add`, `decimal_sub`, `decimal_mul`, `decimal_pow2`, window function `decimal_sum`, and collation `decimal`. `Decimal` stores sign, OOM/null/init flags, total digit count, fractional digit count, and an array of base-10 digits.

Parsing and conversion are handled by `decimalNewFromText()`, `decimal_new()`, `decimalFromDouble()`, and `decimalPow2()`. Output is produced by `decimal_result()` or `decimal_result_sci()`. Arithmetic and comparison are implemented by `decimal_cmp()`, `decimal_expand()`, `decimal_add()`, `decimalMul()`, and `decimal_round()`. Aggregate state is a `Decimal` in SQLite aggregate context and is updated by `decimalSumStep()` and `decimalSumInverse()`.

## Control flow

Scalar functions convert inputs to `Decimal`, perform the requested operation, then render text. Text and integer inputs parse directly; floats and 8-byte blobs can be expanded to an exact decimal representation of their IEEE754 binary64 value unless `bTextOnly` forces text interpretation. Addition aligns integer and fractional digit counts, then either adds or subtracts digit arrays depending on signs. Multiplication uses grade-school accumulation into a new digit array and trims some trailing fractional zeros. `decimal_sum` initializes a zero accumulator, adds each non-NULL value, subtracts values for window inverse, and returns the current/final decimal text.

## State and persistence

The extension is stateless except for aggregate/window state owned by SQLite during query execution. All decimal values are heap-allocated and freed after each scalar operation. The collation parses both comparison keys on each comparison and stores no cached state.

## Dependencies and integration points

It depends on SQLite extension APIs, aggregate/window APIs, deterministic/innocuous function flags, and collation registration. It integrates with SQL ordering through `COLLATE decimal` and with window frames through `decimal_sum`.

## Risks

Large inputs can allocate very large digit arrays, bounded by `SQLITE_DECIMAL_MAX_DIGIT`. OOM is propagated through flags in some paths and direct SQLite errors in others. Text parsing is permissive and stops at exponent or unrecognized characters rather than reporting syntax errors. `decimal_cmp()` mutates operands by trimming trailing fractional zeros, which is safe for temporaries but important to know. Float conversion rejects NaN and infinity by returning NULL/OOM-like behavior depending on the caller path. The collation returns equality on parse failure, which can mask invalid numeric text.

## Test signals

Tests should cover signs, leading/trailing zeros, decimal points, exponents, exact binary64 expansion, 8-byte blob conversion, NaN/infinity behavior, addition/subtraction sign combinations, multiplication fractional trimming, significant-digit rounding in `decimal` and `decimal_exp`, `decimal_pow2` bounds, NULL aggregate behavior, window inverse correctness, collation ordering, and digit-limit/OOM paths.
