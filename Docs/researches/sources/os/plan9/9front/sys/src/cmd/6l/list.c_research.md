# File Research: sources/os/plan9/9front/sys/src/cmd/6l/list.c

- Role: Debug/listing formatting and diagnostics for 6l.
- Registers `%R`, `%A`, `%D`, `%S`, and `%P` format handlers.
- `Pconv()` formats `Prog` records with line number and special DATA/INIT/DYNT/TEXT/GLOBL scale formats.
- `Dconv()` formats linker operands, including resolved branch targets via `pcond`, external/static/auto/param symbols, constants, floats, strings, addresses, indirect operands, and indexed operands.
- `Rconv()` maps amd64 register enums to printable names, paralleling the compiler formatter.
- `Sconv()` escapes fixed-size string constants.
- `diag()` prefixes diagnostics with current text symbol when available, increments `nerrors`, and exits after too many errors.
