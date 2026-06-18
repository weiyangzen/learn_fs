# Research: sources/storage-engines/sqlite/ext/misc/zorder.c

## Purpose

`zorder.c` implements two scalar SQL functions for Morton/Z-order transformations. `zorder(X0, X1, ..., XN)` interleaves bits from 2 to 24 integer dimensions into one signed 64-bit Morton code. `unzorder(Z, N, K)` extracts dimension `K` from an `N`-dimensional Morton code.

The extension is useful for compact spatial indexing experiments where multiple integer dimensions need to be mapped into a single sortable key.

## Important APIs, Types, And Functions

- `sqlite3_zorder_init()` registers `zorder` with variable arity and `unzorder` with arity 3.
- `zorderFunc()` validates argument count, reads up to 24 integer coordinates, interleaves the low 63 bits round-robin by dimension, returns the Morton code, then reports an error if any coordinate had remaining high bits.
- `unzorderFunc()` validates `N` in `[2,24]` and `K` in `[0,N-1]`, then collects every `N`th bit from `Z` starting at bit `K` into the result coordinate.

## Control Flow

`zorderFunc` initializes `z` to zero and copies all inputs to a local array. For bit positions 0 through 62, it selects dimension `i % argc`, ORs that dimension's low bit into output bit `i`, then shifts the dimension right. After returning the integer result, it scans dimensions for leftover bits and sets an error if any input was too large to fit in the 63-bit interleaving budget.

`unzorderFunc` performs straightforward validation, then loops `j=K; j<63; j+=N`, moving bits from the Morton code into consecutive bits of `x`.

## State And Persistence Behavior

There is no persistent state. Both functions are pure with respect to SQLite database contents, although they are not registered with deterministic/innocuous flags in this file.

## Dependencies And Integration Points

The file uses SQLite's loadable-extension ABI and scalar function API. It depends only on SQLite integer conversion/result/error helpers and standard string/assert headers. It integrates by registering functions into the current database connection.

## Risks And Edge Cases

- The error message says `"arguments4"`, which appears to be a typo.
- `zorderFunc` calls `sqlite3_result_int64` before checking overflow and then may overwrite it with an error; SQLite should report the later error, but the ordering is unusual.
- Negative inputs shift arithmetically on many C implementations, leaving high bits set and causing a "too large" error after constructing an intermediate code.
- Only 63 bits are used to avoid signed 64-bit sign-bit complications, so capacity per dimension shrinks as dimensions increase.
- Inputs are coerced with `sqlite3_value_int64`; non-integer SQL values follow SQLite conversion rules.

## Test Signals

Tests should verify round trips for 2D, 3D, and 24D values; boundary values that exactly fit the available bit budget; oversized and negative input errors; invalid argument counts for `zorder`; invalid `N` and `K` for `unzorder`; and SQL type coercion behavior. Sorting by `zorder()` over grid points can validate expected Morton ordering.
