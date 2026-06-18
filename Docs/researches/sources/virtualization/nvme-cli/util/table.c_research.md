# File Research: sources/virtualization/nvme-cli/util/table.c

## Role

`table.c` implements a small in-memory table builder and printer for aligned text output. It supports string, integer, unsigned, long, unsigned long, float, and double cells; left, right, and centered alignment; fixed or auto-adjusting column widths; optional column filtering; and printing to stdout or a caller-provided `FILE *`.

## Width And Printing

- `table_get_value_width()` computes the printable width for a `struct value` using `strlen()` for strings and `snprintf()` for numeric types. Floats and doubles use two decimal places.
- `table_print_centered()` calculates left/right padding around a value for a given column width, prints the value according to its type, then pads the right side.
- `table_print_columns()` prints column names using each column's alignment, then prints a separator row of dashes with matching widths.
- `table_print_rows()` prints each row/cell according to the cell alignment and type. LEFT is implemented by negating the printf width; RIGHT is the default behavior.
- `table_print_stream()` prints headers then rows to the supplied stream.
- `table_print()` prints to stdout.

## Table Construction

- `table_create()` allocates a zeroed `struct table`.
- `table_init_with_columns()` combines allocation and `table_add_columns()`; it frees the table on failure.
- `table_add_columns()` allocates and copies all column definitions, duplicates each column name, validates fixed widths are at least the column-name length, sets auto-width columns to the initial name length, and records `num_columns`.
- `table_add_columns_filter()` either delegates to `table_add_columns()` when no filter is supplied or incrementally appends only columns accepted by `filter(name, arg)`.
- `table_get_row_id()` appends a row with `reallocarray()`, allocates its cell array sized to `num_columns`, increments `num_rows`, and returns the new row index.
- `table_add_row()` finalizes a populated row by expanding auto-adjusting column widths to fit the row's values.
- `table_free()` frees string cell values, row cell arrays, the row array, duplicated column names, columns, and the table object.

The file includes a local `reallocarray()` fallback when `NVME_HAVE_REALLOCARRAY` is not set, with multiplication overflow checking.

## Dependencies

Uses standard C memory/string/stdio APIs, `nvme-print.h` for errors, and `table.h` for data types. It relies on `fallthrough` from project headers/compiler support.

## Notable Edge Cases

- In `table_get_row_id()`, after reallocating `t->rows`, the allocation check for the new row's cell array uses `if (!t->rows->val)` rather than checking `t->rows[row].val`. This only checks row zero's `val` and can miss allocation failure for later rows.
- If `table_get_row_id()` fails to allocate the cell array after growing `t->rows`, it returns `-ENOMEM` without rolling back the reallocated row storage.
- `table_add_columns()` sets `t->num_columns` only after all columns succeed; failure cleanup iterates from the current `col` down to zero. For some failure points, the current column name may not have been initialized.
- Width calculation is byte-oriented, not display-cell-oriented; multibyte or wide Unicode strings may align incorrectly.
- String setters duplicate strings and `table_free()` owns those duplicates.

## Research Notes

The intended caller sequence is: create/init table, get a row id, set every desired cell in that row, call `table_add_row()` to update widths, print, then free. Auto-width behavior depends on `table_add_row()`, so skipping it can produce narrow columns.
