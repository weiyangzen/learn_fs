# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/hdr.h

## Purpose

`hdr.h` is the shared internal header for the `tcs` conversion pipeline. It defines global converter state, the converter descriptor type, input/output function signatures, buffering constants, and shared error-substitution constants.

## Contents

- External global flags/counters:
  - `squawk`, `clean`, `file`, `verbose`
  - `ninput`, `noutput`, `nrunes`, `nerrors`
- Converter flags:
  - `From = 1`
  - `Table = 2`
  - `Func = 4`
- `struct convert`, containing:
  - charset name
  - descriptive chatter text
  - flags
  - data pointer
  - function pointer
- Function pointer typedefs:
  - `Fnptr`
  - `Infn`
  - `Outfn`
- Shared conversion declarations:
  - `conv`
  - `outtable`
  - `fixsurrogate`
  - UTF and ISO-UTF input/output functions
  - `warn`
- Buffering:
  - `N = 10000`
  - external `Rune runes[N]`
  - external `char obuf[UTFmax*N]`
- Output dispatch macro:
  - `OUT(out, r, n)` dispatches either to `outtable` for table converters or to an output function for functional converters.
- Error constants:
  - `BADMAP = 0xFFFD`
  - `BYTEBADMAP = '?'`
  - `ESC = 033`

Full-file validation:
- Lines: 42
- Bytes: 1138
- SHA-256: `d17d303cf25059b54952205dfacc17a671ee929becedd7d02f45f9c5c2364ce4`

## Integration Points

`hdr.h` is included by converter implementation files such as `conv_gbk.c` and by the main `tcs.c` driver. It assumes Plan 9 base headers have already provided types/macros such as `Rune` and `UTFmax`.

## Important Notes

The `OUT` macro is central to the pipeline: input converters emit `Rune` batches without caring whether the destination charset is implemented as a simple table or a function. Since it is a macro with control flow and casts, changes to `struct convert` flags or function signatures would affect most converter modules.
