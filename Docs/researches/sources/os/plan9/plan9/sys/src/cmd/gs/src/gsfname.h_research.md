# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.h

## Role

Declares parsed file-name representation and file-name parsing helpers.

## Main Data

`gs_parsed_file_name_t` records the allocator used for a copied C string, resolved IO device, file-name pointer, and length. The name may initially be unterminated.

## Main API

Declares `gs_parse_file_name`, `gs_parse_real_file_name`, `gs_terminate_file_name`, and `gs_free_file_name`.

## Contract

Callers must construct parsed names through the parser helpers rather than filling the structure manually. `gs_parse_real_file_name` also converts the result to a C string.

## Dependencies

Forward-declares `gx_io_device`; relies on Ghostscript memory and string types.
