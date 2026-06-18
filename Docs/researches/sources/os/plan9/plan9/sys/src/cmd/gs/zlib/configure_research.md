# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/configure

## Purpose
Portable shell configuration script for zlib compiler flags, shared/static library selection, feature detection, and Makefile generation.

## Public Surface
Command-line options include `--shared`, `--prefix`, `--exec_prefix`, `--libdir`, `--includedir`, and help.

## Implementation Notes
- Extracts zlib version pieces from `zlib.h`.
- Defaults archive tools, install prefixes, shared extension, and static build mode.
- Detects gcc and platform-specific shared-library flags for Linux/GNU, Cygwin/OS2, QNX, HP-UX, Darwin, IRIX, OSF1, SCO, SunOS, AIX, and generic Unix.
- Tests shared-library support by compiling and linking a temporary test.
- Detects `unistd.h` and rewrites `zconf.h` from `zconf.in.h`.
- Probes `vsnprintf`/`snprintf` availability and return-value behavior, adding fallback macros and printing security warnings for unsafe fallbacks.
- Detects `errno.h`, `mmap`, and assembler symbol underscore behavior.
- Cleans temporary test files and rewrites `Makefile` from `Makefile.in` with selected variables.

## Dependencies
Requires POSIX shell, compiler, `sed`, `uname`, optional `nm`, source headers, and writable build directory.

## Risks and Notes
- Uses compile/link probes with generated temporary files in the source directory.
- Falling back to `sprintf`/`vsprintf` is explicitly warned as a string-format security risk.
- Filesystem relevance: build-time file generation and installation configuration only.
