# sources/storage-engines/sqlite/ext/misc/series.c

Purpose: implements the eponymous `generate_series` virtual table for signed 64-bit integer sequences with hidden `start`, `stop`, and `step`.

Important APIs/types/functions: `series_cursor` stores original and adjusted bounds, step, current value, and direction. Overflow-safe helpers are `span64()`, `add64()`, and `sub64()`. Planner/execution methods are `seriesBestIndex()`, `seriesFilter()`, `seriesNext()`, `seriesColumn()`, and `seriesRowid()`.

Control flow: best-index encodes hidden-column constraints, value/rowid inequalities, LIMIT/OFFSET, and order-by into `idxNum`. Filtering reads arguments, applies defaults, intersects value constraints, aligns endpoints to step, reverses for consumed order-by, applies limit/offset, and positions the first row.

State and persistence: cursor-local only; read-only virtual table.

Dependencies/integration: SQLite virtual table support, SQLite 3.8.12+, optional math helpers and compile-time zero-argument behavior.

Risks/test signals: 64-bit extremes, negative/zero steps, float constraint rounding, missing-start planner errors, limit/offset arithmetic, and order reversal. Test positive/negative ranges, boundary values, value-only constraints, nulls, rowid constraints, and consumed ascending/descending orders.
