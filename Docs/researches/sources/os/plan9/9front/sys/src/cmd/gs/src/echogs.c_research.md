# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/echogs.c

## Scope

Portable build utility similar to `echo`, used to work around shell and utility incompatibilities when generating Ghostscript build artifacts.

## Key Behavior

- Supports output to stdout, write, append, binary file modes, optional filename extension, hex output, and newline suppression.
- Parses command switches for literal strings, spaces, uppercase conversion, dates, output filename/base-name insertion, reading arguments from stdin/files, raw file copying, and treating literals as hex.
- Uses `hputc` and `hputs` for hex-encoded output mode.
- Interactive mode reads one line at a time from stdin or a named file and treats each line as an argument.

## Dependencies

Uses `stdpre.h`, stdio/stdlib, ctype/string/time APIs, and Ghostscript-style `exit_OK` / `exit_FAILED` constants.

## Risks And Invariants

- Fixed-size `fname[100]` and `line[1000]` buffers require generated inputs to stay within expected build-system limits.
- Hex parsing emits a byte every two hex digits but does not explicitly reject odd-length hex strings.
- File option parsing mutates the argument vector for the `-w-` / `-a-` form.
