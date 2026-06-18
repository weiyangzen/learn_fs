# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.h

Declares Ghostscript configuration constants and resource-table access macros.

Key contents:
- Includes `gconfigv.h`.
- Defines `CONFIG_CONST` based on `SYSTEM_CONSTANTS_ARE_WRITABLE`.
- Declares exported configuration constants:
  - build time
  - copyright
  - product/product family
  - revision and revision date
  - serial number
  - documentation directory
  - default library path
  - initialization file
- Provides macros to declare resource tables without importing all dependent types:
  - `extern_gx_device_halftone_list`
  - `extern_gx_image_class_table`
  - `extern_gx_image_type_table`
  - `extern_gx_init_table`
  - `extern_gx_io_device_table`
  - `extern_gs_lib_device_list`
  - `extern_gs_find_compositor`
- Declares count variables for image class/type tables and IO devices.

Important implementation notes:
- The file intentionally avoids depending on Ghostscript base types directly in processed declarations because it may be included before `stdpre.h`.
- The extern macros defer type requirements to users that already have the corresponding type definitions in scope.
