# File Research: sources/os/plan9/plan9/sys/src/cmd/db/command.c

Command decoder for the Plan 9 `db` debugger.

Key responsibilities:
- Maintains command state globals: `dot`, `dotinc`, address/count flags, last command, format defaults, and `ditto`.
- `command()` parses an optional address expression, optional count, command verb, and semicolon-separated command list.
- Supported command verbs include:
  - `/`, `?`, `=` for memory/text/literal examination.
  - `>` to assign `dot` to a register.
  - `!` shell escape.
  - `$` trace/status commands.
  - `:` process control commands.
- `acommand()` handles examine/search/write subcommands:
  - `m` map print
  - `l`/`L` source search by 2/4-byte value
  - `w`/`W` write 2/4-byte values
  - otherwise format scan via `scanform()`.
- `cmdsrc()` scans mapped memory for masked 2-byte or 4-byte values.
- `cmdwrite()` writes values to a map and prints before/after-style output.
- `regname()` collects alphanumeric register names.
- `shell()` runs `/bin/rc -c` on the rest of the input line.

Important interactions:
- Uses expression parser from `expr.c`, input from `input.c`, and format execution from `format.c`.
- Uses `Map` operations from libmach helpers (`get2`, `get4`, `put2`, `put4`).
- Process execution commands delegate to `subpcs()`.

Research notes:
- `command()` saves and restores input state when executing a passed-in buffer, enabling recursive command execution.
- `executing` prevents nested `:` process-control execution.
