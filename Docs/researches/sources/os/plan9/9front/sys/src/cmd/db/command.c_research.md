# File Research: sources/os/plan9/9front/sys/src/cmd/db/command.c

Purpose: Top-level command decoder for the Plan 9 `db` debugger.

Key behavior:
- `command()` parses optional address, optional count, and command character, preserving last command defaults.
- `/`, `?`, and `=` dispatch to `acommand()` for memory/symbol/literal examination.
- `>` writes current dot value to a register.
- `!` executes a shell command.
- `$` runs debugger meta commands through `printtrace()`.
- `:` runs process-control commands through `subpcs()`, guarded by `executing`.
- `acommand()` handles map display (`m`), search (`l`/`L`), writes (`w`/`W`), or format scanning.
- `cmdsrc()` searches memory for 16-bit or 32-bit values with optional mask.
- `cmdwrite()` writes 16-bit or 32-bit values to the selected map and prints the resulting value.
- `regname()` parses multi-character register names.
- `shell()` executes `/bin/rc -c` with the rest of the input line.

Notable details:
- Default formats are `eqformat = "z"` and `stformat = "zMi"`.
- `dot`, `dotinc`, `adrval`, `cntval`, and related flags are global debugger cursor state.
