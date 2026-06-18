# File Research: sources/virtualization/open-iscsi/usr/local_strings.h

## Purpose
`local_strings.h` declares the local growable buffer abstraction implemented by `local_strings.c`.

## Exports
It defines `struct str_buffer` with `allocated_length`, `data_length`, and `buffer`, and declares initialization, allocation, free/reset, enlarge, prefix removal, truncate, data pointer, data length, and unused length helpers.

## Integration Notes
The header does not include `<stddef.h>` itself, so users need `size_t` available before inclusion through another header or source include.
