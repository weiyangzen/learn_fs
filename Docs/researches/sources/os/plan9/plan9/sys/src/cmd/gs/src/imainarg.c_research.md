# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.c

Implements command-line parsing and dispatch for Ghostscript.

Key points:
- `gs_main_init_with_args` initializes argument reading with `@` file expansion, calls `gs_main_init0`, reads `GS_LIB` and `GS_OPTIONS`, sets default library path, prescans help/version, processes switches and filenames, then finishes with `gs_main_init2`.
- `gs_main_run_start` runs `systemdict /start get exec`.
- `swproc` handles stdin modes, PostScript argv passing, debug/log flags, run-string buffer sizing, inline code, file execution, geometry/resolution, help/version, library paths, memory/name-table settings, search policy, quiet startup, `-d/-D`, `-s/-S`, undefine, and debug hooks.
- `-d` parses a PostScript token; executable names are restricted to `null`, `true`, or `false`.
- `-sstdout=...` supports stdout redirection to files or stderr.
- `argproc`, `run_buffered`, and `runarg` dispatch file/direct/buffered execution and escape file/argument strings into PostScript snippets.
- Error/finish behavior flushes output/display and dumps stacks for unexpected interpreter errors.
- Help output prints revision, usage, emulators, sorted devices, search paths, and documentation/bug-report text.

Research relevance:
- User-facing CLI translation layer from argv/env into interpreter state and PostScript execution.
