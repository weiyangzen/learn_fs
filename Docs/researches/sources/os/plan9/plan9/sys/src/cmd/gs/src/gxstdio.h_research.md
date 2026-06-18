# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstdio.h

Small Ghostscript compatibility header providing a stdio back door for contributed drivers.

Key contents:
- Includes `gsio.h`.
- Undefines and remaps `stdin`, `stdout`, and `stderr` to Ghostscript-managed `gs_stdin`, `gs_stdout`, and `gs_stderr`.
- Undefines `fgetchar`.

Research notes:
- The comment says the core library and interpreter do not use standard streams directly, but some contributed drivers still write to stdout/stderr.
- This is a portability shim, not a full stdio wrapper.
