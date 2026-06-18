# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spsdf.h

Declares PostScript/PDF output syntax helpers and parameter-printer state.

Key points:
- Defines flags controlling string output: `PRINT_BINARY_OK`, `PRINT_ASCII85_OK`, and `PRINT_HEX_NOT_OK`.
- Declares `s_write_ps_string` and `s_alloc_position_stream`.
- Defines `param_printer_params_t` for prefix/suffix/item formatting and allowed print modes.
- Defines `printer_param_list_t`, a concrete param-list implementation with stream, params, and `any` state.
- Declares allocation, initialization, release, and free functions for parameter printers.

Research relevance:
- Interface for serializing PostScript/PDF symbolic data and parameter dictionaries.
