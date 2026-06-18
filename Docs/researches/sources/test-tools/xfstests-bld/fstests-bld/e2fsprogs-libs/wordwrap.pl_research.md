# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/wordwrap.pl

Purpose: `wordwrap.pl` wraps dependency or makefile-style lines to about 78 columns while preserving comments and adjusting a few source-path references.

Important APIs, types, and functions: Perl reads stdin line-by-line. It skips comment lines and blank lines, splits other lines on whitespace, rewrites selected `$(srcdir)/.../version.h` and `com_err.h` paths to `$(top_srcdir)/...`, and emits words with backslash-newline continuations when the line length exceeds 78.

Control flow: for each non-comment nonblank line, initialize `linelen`, iterate words, optionally print a space, compute next word length, emit `\\\n ` when wrapping, then print the word and final newline.

State and persistence: pure stream transformer; no persistent state or file I/O beyond stdin/stdout.

Dependencies and integration points: used in build dependency generation cleanup where wrapped Makefile dependency lines are desired. It is tied to e2fsprogs source layout path rewrites.

Risks: `split` without assignment uses `@_`, which works in this script but is terse. Blank lines are dropped rather than preserved. It treats all whitespace as separators, so quoted values are not preserved.

Test signals: feed dependency lines longer than 78 chars, comment lines, blank lines, and the specific version/com_err path patterns.
