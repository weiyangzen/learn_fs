# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/builtin.c

Builtin Acid functions for process control, file access, formatting, regex, tracing, conversion, and printing.

Key responsibilities:
- Installs builtins into the symbol table.
- Provides process operations: `newproc`, `startstop`, `waitstop`, `start`, `stop`, `kill`, `status`, `reason`, `setproc`.
- Provides stack/symbol operations: `follow`, `funcbound`, `filepc`, `pcfile`, `pcline`, `strace`.
- Provides script/module operations: `interpret`, `include`, `rc`.
- Provides file and access helpers: `readfile`, `getfile`, `access`, `error`.
- Provides conversions: `atof`, `atoi`, `itoa`, `fmt`, `fmtof`, and `fmtsize`.
- Converts libmach memory maps to Acid lists.
- Implements regex matching and list flattening for builtin argument handling.
- Implements Acid printing through `print`, `printto`, and atom/list formatting.

Dependencies:
- Uses libmach process/memory/symbol APIs, Plan 9 `/proc` controls through helper functions, regex library, Bio, and Acid AST/list helpers.

Notable risks:
- Builtins expect strict argument counts/types and report errors through the interpreter’s longjmp path.
- `rc` and process/file operations interact with the host namespace and target process state.
