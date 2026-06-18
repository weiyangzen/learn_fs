# File Research: sources/virtualization/nvme-cli/util/table.h

## Role

`table.h` declares the table data model, inline value setters, and public table functions implemented in `table.c`.

## Data Model

- `AUTO_WIDTH` is `INT_MAX`, used as a sentinel for auto-adjusting column width.
- `enum fmt_type` identifies cell payload type: string, int, unsigned, long, unsigned long, float, double.
- `enum alignment` identifies right, left, or centered alignment.
- `struct value` stores a union payload plus alignment and format type.
- `struct table_row` owns a dynamically allocated `struct value *val` array.
- `struct table_column` stores duplicated column name, alignment, width, and internal `auto_adjust` flag.
- `struct table` owns dynamic column and row arrays plus counts.

## Inline Setters

Bounds-checking setters:

- `table_set_value_str()` checks row/column bounds, duplicates the input string, stores alignment and `FMT_STRING`.
- `table_set_value_int()` checks bounds and stores `FMT_INT`.
- `table_set_value_unsigned()` checks bounds and stores `FMT_UNSIGNED`.
- `table_set_value_long()` checks bounds and stores `FMT_LONG`.

Unchecked setters:

- `table_set_value_unsigned_long()`
- `table_set_value_float()`
- `table_set_value_double()`

The unchecked setters directly index the row and column arrays and return `void`, so callers must validate indices before use.

## Public Functions

- `table_create()`
- `table_add_columns()`
- `table_add_columns_filter()`
- `table_get_row_id()`
- `table_add_row()`
- `table_print_stream()`
- `table_print()`
- `table_free()`
- `table_init_with_columns()`

## Dependencies

Includes `<stdio.h>`, `<stdbool.h>`, and `<limits.h>`. The inline setters use `strdup()`, `EINVAL`, and `ENOMEM` but this header does not include `<string.h>` or `<errno.h>` directly, so it relies on surrounding includes through project headers or translation units.

## Research Notes

The header exposes concrete structs rather than an opaque table handle. That makes the API lightweight but allows callers to mutate internals such as `auto_adjust` or counts. The comment explicitly says `auto_adjust` is internal and should not be used by callers.
