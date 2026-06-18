# File Research: sources/os/plan9/9front/sys/src/cmd/acid/builtin.c

Built-in Acid functions for conversion, printing, files, process control, maps, stack traces, regex, shell execution, and debugger metadata.

Key responsibilities:
- Registers builtins in the symbol table and records the default `print` call node.
- Implements conversions: `atoi`, `atof`, `itoa`, `fmt`, `fmtof`, `fmtsize`.
- Implements printing to stdout or files and atom/list formatting.
- Implements file reading as strings or lists of lines.
- Implements debugger process controls: `newproc`, `setproc`, `start`, `stop`, `waitstop`, `startstop`, `kill`, `status`.
- Implements source/PC helpers: `filepc`, `pcfile`, `pcline`, `fnbound`, `follow`, `reason`, `strace`.
- Implements map inspection/update through `map()`.
- Implements `include()` and `interpret()` for loading/evaluating Acid source.
- Implements shell command execution through `rc()`.
- Implements list membership match, regexp matching, sysr1, access checks, and field splitting.

Important behavior:
- `flatten()` converts comma/OLIST argument trees into positional arrays.
- `patom()` interprets Acid format characters and uses mach disassembly for `i`/`I`.
- `map()` can mutate existing map segment base/end/file offset when given a 4-element list.
- Builtin calls validate argument counts and types explicitly.

Dependencies:
- Uses Plan 9 `mach` library, process control helpers from other Acid files, regex, bio, and global `bout`.

Notable risks:
- `acidfmt()` has delicate percent-format rewriting logic for `itoa`.
- `readfile()` allocates based on file length or 8192 default and reads once; it may not read growing/streaming files fully.
- `printto()` replaces global `bout` temporarily, so error unwinding must restore IO state.
