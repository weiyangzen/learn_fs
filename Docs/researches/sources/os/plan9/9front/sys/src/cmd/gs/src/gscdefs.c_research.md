# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.c

## Role

`gscdefs.c` defines Ghostscript configuration scalar variables. In this source tree, its contents are identical to `gscdef.c`.

This is application configuration, not filesystem implementation.

## Defined Symbols

- `gs_buildtime`
- `gs_copyright`
- `gs_productfamily`
- `gs_product`
- `gs_program_name()`
- `gs_revision`
- `gs_revision_number()`
- `gs_revisiondate`
- `gs_serialnumber`
- `gs_doc_directory`
- `gs_lib_default_path`
- `gs_init_file`

## Build-Time Inputs

- Uses makefile/generated symbols from `gconfigd.h`.
- Falls back to built-in values for product family, copyright string, build time, and serial number when those macros are absent.
- Requires `GS_REVISION`, `GS_REVISIONDATE`, `GS_DOCDIR`, `GS_LIB_DEFAULT`, and `GS_INIT`.

## Relationship To `gscdef.c`

- This file appears to be a duplicate copy of `gscdef.c`.
- If both are compiled into the same link target, they would define the same global symbols and cause duplicate-definition conflicts. The build likely selects one variant.

## Dependencies

- Includes `std.h`, `gscdefs.h`, and `gconfigd.h`.

## Notable Risks

- The duplicate with `gscdef.c` requires build-system care.
