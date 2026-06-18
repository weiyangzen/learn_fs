# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/doprint.c

- Role: Reimplements a compact Plan 9-style formatting engine for Unix-hosted u9fs.
- Key functions: `doprint` parses format strings; `fmtinstall` registers custom converters; `numbconv`, `strconv`, `Strconv`, `cconv`, `sconv`, `percent`, and `column` implement core verbs.
- State: Global `printcol` tracks output columns; `fmtalloc` maps format characters to converter callbacks.
- Integration: Backing formatter for `print.c`, `u9fs.c` fatal/log output, and custom `%F`, `%D`, `%M` protocol diagnostics.
- Risks/notes: Lock macros are no-ops and buffers are caller-owned; fine for the program’s style, but not generally thread-safe.
