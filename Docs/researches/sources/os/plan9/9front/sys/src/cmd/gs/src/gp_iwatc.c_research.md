# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_iwatc.c

Intel/Watcom C platform routines for DOS-like Ghostscript builds.

Key behavior:
- Initializes a SIGFPE handler that reports numeric exceptions and exits.
- Provides no-op cleanup and direct `exit` termination.
- Stubs persistent cache operations.
- Opens printer output through `stdprn`, `PRN`, or a named file, with special handling to reopen `stdprn` in binary mode for Watcom newline behavior.
- Creates scratch files under the configured temp directory using `mktemp` and `gp_fopentemp`.
- Provides plain `fopen` as `gp_fopen`.
- Stubs native font enumeration.

Notable dependencies:
- Uses DOS/Watcom file APIs, `setmode`, `dup`, and `fdopen`.
- Relies on replacement `mktemp` from `gp_mktmp.c`.

Research notes:
- Persistent cache and native font enumeration are not implemented.
