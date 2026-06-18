# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmainc.c

Console-only Ghostscript shared-library front end.

Key points:
- Minimal `libgs` client for command-line execution without the display callback.
- Provides stdio callbacks using POSIX `read` for stdin and `fwrite`/`fflush` for stdout/stderr.
- Runs Ghostscript startup by invoking `systemdict /start get exec`.
- Uses the same `gsapi_*` lifecycle and exit-code mapping pattern as `dxmain.c`.

Dependencies and interactions:
- Includes `iapi.h` and `ierrors.h`.
- Does not create or configure a display device.

OS/filesystem relevance:
- Direct use of process stdio only.
- No filesystem-specific logic beyond Ghostscript’s arguments being handled by the library.
