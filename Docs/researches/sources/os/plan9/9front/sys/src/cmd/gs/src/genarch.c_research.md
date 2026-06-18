# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/genarch.c

Build-time generator for `arch.h`, deriving compiler and machine architecture parameters.

Key behavior:
- Writes scalar alignment macros for short, int, long, pointer, float, double, and `jmp_buf`.
- Writes scalar size macros, float/double mantissa estimates, and unsigned max-value macros.
- Detects IEEE float representation by inspecting bit patterns for 0, 1, and -1.
- Estimates primary and secondary cache sizes by timing repeated `memset` calls across larger buffers.
- Emits endian, pointer signedness, arithmetic right-shift behavior, full-width long shift behavior, and negative-division semantics.

Notable dependencies:
- Uses `stdpre.h` and standard C headers including `string.h`, `time.h`, and `setjmp.h`.
- Relies on Ghostscript build macros such as `private`, `size_of`, `exit_OK`, and `exit_FAILED`.

Research notes:
- It writes to the output file named by `argv[1]` rather than stdout for old make-tool compatibility.
- The cache-size detection is heuristic and build-host dependent.
