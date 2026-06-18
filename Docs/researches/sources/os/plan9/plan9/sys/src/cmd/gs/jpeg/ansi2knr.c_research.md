# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ansi2knr.c

Utility that converts ANSI C function definitions to K&R-style definitions for traditional C compilers.

Key behavior:
- Contains a large embedded license/comment preamble, then portable C implementation guarded for systems with or without GNU `configure` output.
- `main` accepts `ansi2knr input_file [output_file]`, supports the historical `--varargs` switch, emits a `#line` directive, reads the input into a fixed 5000-byte buffer, and converts only recognized function definitions.
- `skipspace` skips whitespace and C comments forward or backward.
- `writeblanks` overwrites spans with spaces while preserving newlines.
- `test1` detects candidate function definitions by requiring an identifier at the left margin, a non-keyword function name, a parenthesized argument list, and suitable trailing syntax.
- `convert1` rewrites a detected ANSI-style header into K&R form by extracting argument names, erasing embedded prototype arguments, handling function-pointer/array declarators, handling `void` parameter lists, and converting varargs to `va_alist`/`va_dcl`.
- Avoids converting prototypes because Ghostscript/IJG declaration macros resemble prototypes and can confuse the parser.

Dependencies:
- Uses stdio, ctype, string APIs, malloc/free, and optional `config.h`.
- Has portability branches for BSD strings, VMS declarations, MSDOS malloc header, K&R library declarations, and `isascii` behavior.

Research notes:
- This is a heuristic source-to-source transformer, not a full C parser.
- It intentionally recognizes only a narrow definition style and can be confused by macros or other left-margin constructs that mimic function definitions.
- The fixed input buffer and repeated string manipulation make it unsuitable for arbitrary modern C without validation.
