# File Research: sources/virtualization/open-iscsi/usr/kern_err_table.h

## Purpose
`kern_err_table.h` declares the kernel iSCSI error-code string conversion function.

## Exports
It exports `const char *kern_err_code_to_string(int);`.

## Integration Notes
This header intentionally has a narrow surface: consumers can stringify kernel error codes without depending on the implementation table.
