# File Research: sources/virtualization/nvme-cli/util/utils.h

## Role

`utils.h` declares the generic binary parsing helpers implemented in `utils.c`.

## Data Structures

- `struct request_data` is packed and contains:
  - `char *field`;
  - `int size`;
  - `int size2`.

`size` and `size2` allow the parser to choose between two layout variants based on the `spec` argument to `generic_structure_parser()`.

`enum field_size` defines named sizes for 16, 8, 7, 6, 4, 3, 2, and 1 byte fields.

## Declared Functions

- `hex_to_int()`
- `hex_to_ascii()`
- `read_binary_file()`
- `generic_structure_parser()`
- `print_formatted_var_size_str()`
- `process_field_size_16()`
- `process_field_size_8()`
- `process_field_size_7()`
- `process_field_size_6()`
- `process_field_size_default()`

## Dependencies

Includes `common.h` and `nvme-print.h`. The function prototypes mention `__u8`, `FILE`, and `struct json_object`, which are expected to be made available through included project headers.

## Research Notes

The comments contain several copy/paste inaccuracies, but the prototypes show the intended ownership model: `hex_to_ascii()` and the `process_field_size_*()` functions return allocated strings; `read_binary_file()` returns an allocated data buffer. Callers must free those results.
