# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/genarch.c

Read status: complete.

Purpose: build-time generator for `arch.h`, a mechanically generated header describing compiler and machine architecture properties needed by Ghostscript.

Main logic:
- Opens the output file named by `argv[1]`.
- Emits scalar alignment constants by measuring offsets in small structs.
- Emits scalar size constants, pointer size, float/double size, and mantissa-bit assumptions.
- Detects IEEE single-precision floats by inspecting bit patterns for `0.0`, `1.0`, and `-1.0`.
- Emits unsigned maximum constants using textual hexadecimal masks to avoid compiler warning/extension problems.
- Estimates primary and secondary cache sizes by timing repeated `memset` calls over increasing buffer sizes.
- Emits endian, signed-pointer comparison, arithmetic right-shift behavior, full-width shift behavior, and negative division truncation behavior.

Important functions:
- `section` prints comment section headers.
- `time_clear` times zero-filling a buffer.
- `define` and `define_int` write `#define` lines.
- `print_ffs` prints all-`ff` byte masks.
- `ilog2` computes rounded-up log2-style size encodings used by Ghostscript.

Filesystem/storage relevance:
- No runtime filesystem behavior. It writes a generated header at build time.

Notable behavior and risks:
- Assumes `argv[1]` exists; no `argc` validation.
- Cache-size detection is heuristic and time-sensitive.
- Some emitted architecture facts are derived from implementation-defined C behavior, such as signed right shifts and pointer comparisons.
