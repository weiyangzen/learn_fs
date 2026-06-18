# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.c

Implements command-line parsing and dispatch for Ghostscript.

Key points:
- `gs_main_init_with_args`:
  - initializes argument reader with `@` file expansion support
  - calls `gs_main_init0`
  - reads `GS_LIB` and `GS_OPTIONS`
  - sets default library path
  - prescans `--help` and `--version`
  - processes switches and filenames
  - finishes init with `gs_main_init2`
- `gs_main_run_start` runs `systemdict /start get exec`.
- `swproc` handles switches:
  - `-` / `-_` stdin execution modes
  - `--`, `-+`, `-@` command-line args for PostScript program
  - `-A`, `-E`, `-Z`, `-T` debug/log flags
  - `-B` buffered run-string size
  - `-c` inline PostScript code
  - `-f`, `-F` file execution
  - `-g`, `-r` device geometry/resolution
  - `-h`, `-?`, `-v`
  - `-I` library path
  - `-K`, `-M`, `-N` memory/name table settings
  - `-P` current-directory search policy
  - `-q` quiet startup
  - `-d/-D`, `-s/-S` systemdict definitions
  - `-u` undefine name
  - `-X` debug test hook
- `-d` parses a PostScript token; executable names are restricted to `null`, `true`, or `false`.
- `-sstdout=...` supports stdout redirection to files or stderr.
- File execution:
  - `argproc` dispatches direct or buffered execution.
  - `run_buffered` feeds file bytes through suspendable `run_string`.
  - `runarg` hex-escapes file/argument strings before building PostScript snippets.
- Error/finish behavior:
  - flushes output and display
  - dumps stacks for unexpected interpreter errors
- Help output prints revision, usage, emulators, sorted device list, search paths, and docs/bug-report trailer.

Dependencies and interactions:
- Wraps `imain.c` API.
- Uses `gsargs`, platform env/file APIs, scanner, stacks, dictionaries, and device registry.

Risks and notes:
- Several switches initialize only as much of the interpreter as needed.
- Path and option environment inputs are copied into Ghostscript heap allocations.
- Help device list sorting falls back to unsorted output if allocation fails.

Research relevance:
- User-facing CLI semantics and translation layer from argv/env into interpreter state and PostScript snippets.
