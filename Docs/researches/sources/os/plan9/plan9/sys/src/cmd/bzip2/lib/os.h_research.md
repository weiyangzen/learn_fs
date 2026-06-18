# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/os.h

Portability header for the embedded bzip2 library. It defaults to generic Unix, detects non-Cygwin Win32, and switches to Plan 9 when `PLAN9` is defined.

It includes `unix.h`, `lccwin32.h`, or `plan9.h` based on the selected platform, defines `NORETURN` for GCC, and establishes bzip2’s basic integer and boolean typedefs: `Char`, `Bool`, `UChar`, `Int32`, `UInt32`, `Int16`, `UInt16`, and `IntNative`.

The Plan 9 copy is modified from upstream and provides a stable type substrate for all bzip2 sources in this directory.
