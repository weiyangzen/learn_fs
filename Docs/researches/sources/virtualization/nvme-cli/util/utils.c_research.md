# File Research: sources/virtualization/nvme-cli/util/utils.c

## Role

`utils.c` implements Micron-origin utility helpers for hex conversion, binary file loading, formatted raw-data output, and generic parsing of structured binary data into text or JSON. It is compiled only for non-Windows builds according to `util/meson.build`.

## Hex And File Helpers

- `hex_to_int()` converts a single hexadecimal character to integer value, returning `-1` for invalid characters.
- `hex_to_ascii()` converts a hex string to allocated ASCII text. It handles odd-length input by treating the first nibble as a standalone value and processes pairs from the end toward the start.
- `read_binary_file()` builds a file path from optional directory and file name, retries `fopen()` up to `retry_count`, determines size with `fseek()`/`ftell()`, allocates a buffer, reads the entire file, and returns the allocated buffer plus size through `buffer_size`.
- `print_formatted_var_size_str()` formats raw bytes as uppercase hex and prints `<msg>: <hex>` to the supplied `FILE *` or stdout.

## Field Formatting Helpers

These functions return allocated strings that callers must free:

- `process_field_size_16()` formats 16-byte fields. If the field name contains `GUID`, it prints high 64 bits then low 64 bits. Otherwise it suppresses leading high-half zeros when possible.
- `process_field_size_8()` has special handling for field names containing `Boot SSD Spec Version`, `Firmware Revision`, and `Timestamp`; otherwise it formats a little-endian 64-bit hex value.
- `process_field_size_7()` copies seven little-endian bytes into an eight-byte buffer and formats the resulting 64-bit value.
- `process_field_size_6()` has special handling for `DSSD Spec Version`; otherwise it combines a 32-bit low part and 16-bit high part into a 48-bit value.
- `process_field_size_default()` formats an arbitrary byte field as `0x` followed by uppercase bytes in buffer order.

## Generic Structure Parser

`generic_structure_parser()` walks an array of `struct request_data` descriptors:

- selects each field's size from `size` or `size2` depending on `spec`;
- skips zero-sized fields and null field names;
- formats the current buffer offset based on the size-specific helpers;
- advances `offset` by the selected size;
- skips output for field names containing `Reserved`;
- emits to a JSON object when `stats` is non-NULL, otherwise to `fp` when supplied, otherwise stdout.

JSON output uses `json_object_add_value_string()`, which becomes a no-op in non-JSON builds.

## Dependencies

Includes `utils.h`, `types.h`, `json.h`, and `cleanup.h`. It depends on project endian helpers and output helpers pulled in by `common.h`/`nvme-print.h` through `utils.h`.

## Notable Edge Cases

- `hex_to_ascii()` does not validate `hex_to_int()` results before composing bytes, so invalid hex characters can produce negative-derived byte values.
- `hex_to_ascii()` does not check `malloc()` failure before writing to `text`.
- `read_binary_file()` leaks `buffer` when `fread()` returns a short read.
- In `read_binary_file()`, if `buffer_size <= 0`, the allocated path is not freed when `data_dir_path` was provided.
- `print_formatted_var_size_str()` does not check `calloc()` failure before using `strcat()`.
- Several field processors cast unaligned byte-buffer addresses to integer pointers, which can be problematic on architectures that fault on unaligned access.
- `generic_structure_parser()` trusts descriptor sizes and does not receive the total buffer length, so it cannot bounds-check reads.
- Special behavior is driven by substring matching on field names, coupling parser semantics to display labels.

## Research Notes

This file is a schema-lite binary parser: descriptors provide field names and sizes, while hardcoded field-name substrings trigger special decoding. It is convenient for vendor log pages but should be used only when the descriptor list and backing buffer length are known to be correct by the caller.
