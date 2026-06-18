# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdef.c

Defines Ghostscript build/configuration scalar values.

Key contents:
- Includes `std.h`, `gscdefs.h`, and generated/config header `gconfigd.h`.
- Defines `gs_buildtime`, defaulting to `0` unless `GS_BUILDTIME` is supplied.
- Defines copyright, product family, and product strings:
  - `gs_copyright`
  - `gs_productfamily`
  - `gs_product`
- Provides `gs_program_name()`.
- Defines `gs_revision` from required makefile macro `GS_REVISION`.
- Provides `gs_revision_number()`.
- Defines `gs_revisiondate` from required makefile macro `GS_REVISIONDATE`.
- Defines `gs_serialnumber`, defaulting to `42` unless configured.
- Defines installation strings:
  - `gs_doc_directory`
  - `gs_lib_default_path`
  - `gs_init_file`

Important implementation notes:
- Uses `CONFIG_CONST`, controlled by `gscdefs.h`, to optionally make system constants writable for applications that require it.
- This file is build-configuration glue, not runtime algorithmic code.
- In this checkout, `gscdef.c` and `gscdefs.c` have identical contents.
