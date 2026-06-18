# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/hdr.h

This is the shared internal header for Plan 9's `tcs` character-set converter. It defines global state, converter descriptors, function pointer types, common buffers, error sentinels, and portability macros.

Key contents:
- Declares global flags and counters: `squawk`, `clean`, `file`, `verbose`, `ninput`, `noutput`, `nrunes`, and `nerrors`.
- Defines converter capability flags: `From`, `Table`, and `Func`.
- Defines `struct convert` with converter name, description text, flags, data pointer, and function pointer.
- Declares converter registry `convert[]` and lookup helper `conv(char *, int)`.
- Defines input/output function pointer types and the `outtable`, `utf_*`, and `isoutf_*` interfaces.
- Defines shared block size `N = 10000`, global rune/output buffers, bad-map values, and `ESC`.
- Provides `OUT(out, r, n)` to dispatch either table-based or function-based output conversion.
- Provides Plan 9 versus hosted-C macros for error printing, unused values, and process exit.

Important details:
- `OUT` is central glue: input converters emit batches of runes and let the selected output converter decide whether to use `outtable()` or an output function.
- `BADMAP` is Unicode replacement character `0xFFFD`; `BYTEBADMAP` is `'?'` for byte-oriented fallbacks.
- The header assumes many globals are defined elsewhere in the `tcs` program, especially `tcs.c` and converter modules.
- For non-Plan 9 builds, it maps diagnostics to `fprintf(stderr, ...)` and exits through `exit(n)`.

Filesystem relevance:
- Indirect: provides common text-conversion plumbing for command-line conversion of file and stream contents.
