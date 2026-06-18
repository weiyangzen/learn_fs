# Research: sources/storage-engines/sqlite/ext/misc/wholenumber.c

## Purpose

`wholenumber.c` implements a simple virtual table named `wholenumber` that generates integer values from 1 through 4,294,967,295. It is explicitly marked testing/debug-only, with guidance to use `generate_series()` for real applications.

The table has one column, `value`, and supports simple range constraints and ascending order-by consumption.

## Important APIs, Types, And Functions

- `sqlite3_wholenumber_init()` registers the module when virtual tables are enabled.
- `wholenumber_cursor` stores current `iValue` and maximum `mxValue`.
- `wholenumberConnect()` allocates a minimal `sqlite3_vtab`, declares `CREATE TABLE x(value)`, and marks it `SQLITE_VTAB_INNOCUOUS`.
- `wholenumberBestIndex()` recognizes usable `value >`, `>=`, `<`, and `<=` constraints, assigns argument indexes, omits handled constraints, consumes a single ascending order-by, and sets rough estimated costs.
- `wholenumberFilter()` converts `idxNum` bits and constraint arguments into inclusive cursor start/end bounds.
- `wholenumberNext`, `wholenumberEof`, `wholenumberColumn`, and `wholenumberRowid` implement the generator.

## Control Flow

Planning scans constraints once, selecting at most one lower-bound operator and one upper-bound operator. It encodes the selected operators into `idxNum` bits: `1` for `>`, `2` for `>=`, `4` for `<`, and `8` for `<=`. The lower-bound constraint is assigned argv slot 1 and the upper-bound slot 2 when both exist.

Filtering initializes the cursor to `[1, 0xffffffff]`, then applies lower and upper bounds. Exclusive lower bounds increment the value; exclusive upper bounds decrement the maximum. Scanning increments by one until the current value exceeds the maximum or becomes zero.

## State And Persistence Behavior

There is no persistent state. Each cursor holds its current range. The virtual table object has no custom fields beyond the base allocation. Results are deterministic for a given constraint set.

## Dependencies And Integration Points

The file uses SQLite extension and virtual-table APIs, including `sqlite3_declare_vtab`, `sqlite3_vtab_config(SQLITE_VTAB_INNOCUOUS)`, and planner structures. It is compiled out when `SQLITE_OMIT_VIRTUALTABLE` is defined.

## Risks And Edge Cases

- Unbounded scans are enormous; without an upper bound, estimated cost is set very high but the table can still generate billions of rows.
- Constraint variable names `ltIdx` and `gtIdx` are semantically reversed for lower/upper bounds, which can confuse maintenance.
- Values less than or equal to zero and bounds above `0xffffffff` are clamped through filter logic rather than reported as errors.
- Only ascending order is consumed; descending output is not supported.
- It is not production-oriented and may lag behind `generate_series()` features and safety.

## Test Signals

Tests should query unconstrained and constrained ranges, including `value<10`, `value<=1`, `value>4294967294`, empty ranges, combined exclusive/inclusive bounds, ascending order-by plans, and behavior with negative or oversized bounds. `EXPLAIN QUERY PLAN` can verify constraint omission and order-by consumption.
