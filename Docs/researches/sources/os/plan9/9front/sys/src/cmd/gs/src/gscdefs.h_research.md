# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.h

## Role

`gscdefs.h` declares Ghostscript configuration globals and provides macros for declaring build-generated resource tables without forcing many type definitions into every include site.

This is configuration/resource wiring, not filesystem code.

## Declared Configuration Globals

- `gs_buildtime`
- `gs_copyright`
- `gs_product`
- `gs_productfamily`
- `gs_revision`
- `gs_revisiondate`
- `gs_serialnumber`
- `gs_doc_directory`
- `gs_lib_default_path`
- `gs_init_file`

## Const Control

- Includes `gconfigv.h`.
- Defines `CONFIG_CONST`:
  - empty when `SYSTEM_CONSTANTS_ARE_WRITABLE` is true
  - `const` otherwise

## Resource Declaration Macros

Macros avoid direct dependency on many Ghostscript internal types:

- `extern_gx_device_halftone_list()`
- `extern_gx_image_class_table()`
- `extern_gx_image_type_table()`
- `extern_gx_init_table()`
- `extern_gx_io_device_table()`
- `extern_gs_lib_device_list()`
- `extern_gs_find_compositor()`

Also declares counts:

- `gx_image_class_table_count`
- `gx_image_type_table_count`
- `gx_io_device_table_count`

## Dependencies

- Designed to be included where `stdpre.h` may not be available.
- Macro bodies assume the caller has provided needed types before expanding them.

## Notable Risks

- Resource extern macros are context-sensitive and can fail if expanded before the required types/macros are visible.
