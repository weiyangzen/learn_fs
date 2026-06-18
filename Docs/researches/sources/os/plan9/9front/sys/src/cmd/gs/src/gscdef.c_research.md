# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdef.c

## Role

`gscdef.c` defines Ghostscript configuration scalar variables: product identity, revision metadata, serial number, and installation paths.

This is application configuration, not filesystem implementation.

## Defined Symbols

- Build/product metadata:
  - `gs_buildtime`
  - `gs_copyright`
  - `gs_productfamily`
  - `gs_product`
  - `gs_revision`
  - `gs_revisiondate`
  - `gs_serialnumber`
- Accessors:
  - `gs_program_name()`
  - `gs_revision_number()`
- Installation paths:
  - `gs_doc_directory`
  - `gs_lib_default_path`
  - `gs_init_file`

## Build-Time Inputs

- Includes `gconfigd.h`, which supplies makefile-generated definitions such as:
  - `GS_REVISION`
  - `GS_REVISIONDATE`
  - `GS_DOCDIR`
  - `GS_LIB_DEFAULT`
  - `GS_INIT`
- Provides fallback defaults for:
  - `GS_BUILDTIME`
  - `GS_COPYRIGHT`
  - `GS_PRODUCTFAMILY`
  - `GS_PRODUCT`
  - `GS_SERIALNUMBER`

## Mutability

- Uses `CONFIG_CONST` from `gscdefs.h`.
- Depending on `SYSTEM_CONSTANTS_ARE_WRITABLE`, some variables may be writable rather than `const`.

## Notable Detail

- The default serial number is `42`.
- This file is content-identical to `gscdefs.c` in this group.

## Dependencies

- Includes `std.h`, `gscdefs.h`, and `gconfigd.h`.

## Notable Risks

- Correct compilation depends on the build system defining `GS_REVISION`, `GS_REVISIONDATE`, and path macros.
