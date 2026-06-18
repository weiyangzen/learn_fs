# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ansi2knr.c

Standalone converter from ANSI C function definitions to traditional K&R syntax.

Key points:
- Carries the historical Ghostscript GPL/COPYLEFT text and an explicit note that using the converter during a build does not impose that license on the invoking program.
- Supports `ansi2knr input_file [output_file]`, writing to stdout when no output file is supplied.
- Handles configured and non-configured builds with conditional includes for `config.h`, string headers, `stdlib.h`, `malloc`, VMS/MS-DOS/BSD behavior, and ctype portability.
- Main processing loop reads into a fixed 5000-byte buffer, emits an initial `#line`, identifies possible function definitions with `test1`, and converts recognized definitions with `convert1`.
- `test1` recognizes a non-keyword identifier at the left margin followed by a parenthesized parameter list and either a completed header or a possible multi-line header.
- `skipspace` skips whitespace and block comments in either direction; `writeblanks` erases source spans while preserving line endings.
- `convert1` parses argument declarations, handles function-pointer/array declarator cases, erases embedded prototype parameters, converts `void` argument lists to empty K&R lists, and maps varargs `...` to `va_alist`/`va_dcl`.

Dependencies and interactions:
- Used by old IJG/Ghostscript build flows when the compiler lacks ANSI prototypes; `configure` sets `A2K_DEPS` and `COM_A2K` based on prototype support.
- Its output is a source-level compatibility transform, not part of libjpeg runtime.

Risk notes:
- The function recognizer is intentionally heuristic and comments list constructs that can confuse it, including left-margin macro/function-call lookalikes and macros that alter function-header syntax.
- Uses a fixed buffer and restarts parsing when a multi-line candidate overflows; very long declarations can be emitted unchanged.
- It rewrites C text without a real parser, so modern C constructs beyond the era it targets are not safe inputs.
