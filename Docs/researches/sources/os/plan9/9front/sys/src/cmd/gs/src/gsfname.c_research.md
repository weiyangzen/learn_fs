# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.c

## Role

`gsfname.c` parses Ghostscript file names into optional `%IODevice%` prefixes and real file names, and can copy names into null-terminated C strings.

This is Ghostscript IO naming support, not filesystem implementation code.

## Main Interfaces

- `gs_parse_file_name`
- `gs_parse_real_file_name`
- `gs_terminate_file_name`
- `gs_free_file_name`

## Core Behavior

- Empty names return `undefinedfilename`.
- Plain names without `%` use no explicit IODevice and retain the caller’s string pointer.
- `%device` and `%device%` both refer to a device-only name.
- `%device%name` resolves an IODevice and leaves `name` as the filename part.
- `gs_parse_real_file_name` rejects device-only names with `invalidfileaccess`.
- `gs_terminate_file_name` assigns `iodev_default` when no device is specified and allocates a null-terminated copy.

## Dependencies

Uses Ghostscript memory allocation, error macros, and IODevice lookup through `gs_findiodevice` / `iodev_default`.

## Notable Risks

- `gs_free_file_name` must only be used on structures constructed through these helpers; the header explicitly forbids manual construction.
- Device prefix parsing treats `%device` and `%device%` equivalently, leaving no filename component.
