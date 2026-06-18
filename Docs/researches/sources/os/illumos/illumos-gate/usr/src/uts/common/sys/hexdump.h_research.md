# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hexdump.h

## Role

`hexdump.h` declares the generic hexdump formatter used by kernel and userland code.

## Key Interfaces and Data

- `hexdump_flag_t` controls output: header, address column, ASCII column, alignment, duplicate suppression, and double spacing.
- `HDF_DEFAULT` enables header, address, and ASCII output.
- `hexdump_t` is caller-visible but treated as opaque configuration/state: display address, address width, row width, grouping, indent, marker, optional scratch buffer, and scratch length.
- Initialization/finalization functions are `hexdump_init()` and `hexdump_fini()`.
- Setter functions configure address, address width, row width, grouping, indent, marker, and scratch buffer.
- `hexdump_cb_f` is called per output row with callback argument, row address, string buffer, and length.
- `hexdump()` formats with default state; `hexdumph()` formats with an explicit `hexdump_t`.
- Non-kernel helpers `hexdump_file()` and `hexdump_fileh()` write rows to a `FILE *`.

## Dependencies and Use

The header includes `sys/types.h`, and includes `stdio.h` only outside `_KERNEL`. The stack-allocatable state is useful before kernel memory allocation is available.

## Research Notes

The formatter is callback-based, which lets kernel and userland consumers direct output to different logging or file mechanisms without duplicating formatting code.
