# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.h

## Role

`gsfname.h` defines `gs_parsed_file_name_t` and declares file-name parsing/termination helpers.

This is Ghostscript IO naming API, not filesystem code.

## Main Type

`gs_parsed_file_name_t` stores:

- allocator for an allocated terminated string
- resolved `gx_io_device *`
- filename pointer
- filename length

The filename may be a raw Ghostscript string or a C string, depending on whether it has been terminated.

## Public API

- `gs_parse_file_name`
- `gs_parse_real_file_name`
- `gs_terminate_file_name`
- `gs_free_file_name`

## Important Contract

The header warns callers not to allocate and fill `gs_parsed_file_name_t` manually. The lifecycle depends on the parsing helpers setting the `memory` and `len` fields consistently.
