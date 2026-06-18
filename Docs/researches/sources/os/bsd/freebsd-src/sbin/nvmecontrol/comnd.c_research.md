# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.c

Implements the generic command registration, dispatch, option parsing, help generation, and dynamic module loading framework for `nvmecontrol`.

Key behaviors:
- Maintains a top-level sorted singly linked list of commands.
- Constructor macros in `comnd.h` call `cmd_register()` before `main`.
- `cmd_dispatch()` selects subcommands by `argv[1]` and prints generated usage on missing/unknown command.
- `arg_parse()` builds `getopt_long()` tables from each command’s `struct opts`, writes parsed values directly to option storage, and handles positional `struct args`.
- Supports argument types for booleans, strings, paths, fixed-width unsigned integers, and size strings via `expand_number`.
- `cmd_load_dir()` loads `.so` modules from a directory with `dlopen(RTLD_NOW | RTLD_GLOBAL)`.

Research notes:
- Option storage uses direct pointers to global/static option fields; comments note future desire to use offsets/context objects.
- Numeric parsing uses `strtoul`/`expand_number` with upper-bound checks but limited malformed-string validation for some integer types.
