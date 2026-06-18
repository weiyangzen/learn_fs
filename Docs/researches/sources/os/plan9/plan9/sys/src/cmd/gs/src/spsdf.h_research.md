# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.h

Header for common PostScript/PDF output syntax and parameter printer utilities.

Key contents:
- Defines string-printing flags: `PRINT_BINARY_OK`, `PRINT_ASCII85_OK`, `PRINT_HEX_NOT_OK`.
- Declares `s_write_ps_string` and `s_alloc_position_stream`.
- Defines `param_printer_params_t` for prefix/suffix/item formatting and string print permissions.
- Defines stack-allocatable `printer_param_list_t`.
- Declares allocation, initialization, release, and free helpers for parameter printers.

Notable dependencies:
- Ghostscript parameter API from `gsparam.h`.

Research notes:
- The implementation structure is intentionally exposed because some callers stack-allocate it.
