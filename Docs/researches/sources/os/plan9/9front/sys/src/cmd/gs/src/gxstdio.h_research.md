# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstdio.h

Provides a stdio “back door” for Ghostscript code and contributed drivers.

Key behavior:
- Includes `gsio.h`.
- Undefines C library `stdin`, `stdout`, and `stderr`.
- Redefines them to Ghostscript-managed `gs_stdin`, `gs_stdout`, and `gs_stderr`.
- Undefines `fgetchar`.

Dependencies:
- Depends on Ghostscript I/O redirection definitions from `gsio.h`.

Research notes:
- The file exists for legacy/contributed code that still writes to stdio, even though the core library/interpreter avoid direct stdio use.
- This is preprocessor compatibility glue rather than runtime logic.
