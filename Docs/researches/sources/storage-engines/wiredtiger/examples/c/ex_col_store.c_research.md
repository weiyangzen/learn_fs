# sources/storage-engines/wiredtiger/examples/c/ex_col_store.c

Purpose: demonstrates column-store tables, column groups, indexes, updates, removals, projections, and basic analytics over synthetic weather data.

Important APIs and control flow: defines `WEATHER` with numeric and fixed-string fields. `main` creates `table:weather` with record-number keys, a structured value format, named columns, and several column groups. It generates 100 random records, appends them, prints all rows through a projected table cursor, creates hour and country indexes, calculates min/max temperature over a time range, converts temperatures through the `colgroup:weather:temperature` cursor, recalculates min/max, computes per-country averages through `index:weather:country`, removes Australian rows through the location column group, and recomputes averages.

State and persistence: persists weather rows split across column groups and maintains secondary indexes after creation. `generate_data` seeds from process ID, so content varies per run. Updates through a column group mutate the stored table values; deletes through a column group remove records.

Dependencies and integration: depends on `test_util.h`, standard C random/string/assert APIs, WiredTiger column group/index semantics, and `WT_MIN`/`WT_MAX`.

Risks: `average_data` divides by `count` without guarding zero after a successful initial search; if search finds a country key but later filtering yields zero, this would fail. Random data makes output nondeterministic. Fixed string widths require countries/days to fit.

Test signals: successful scans should terminate with `WT_NOTFOUND`, temperature conversion should update values, and averages after `remove_country` should no longer include AUS records.
