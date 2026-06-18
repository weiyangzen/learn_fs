# File Research: sources/os/plan9/9front/sys/src/cmd/test.c

This is Plan 9 `test` / `[` implementing POSIX-style expression evaluation plus Plan 9 mode predicates.

Expression parser:
- `e()` handles `-o`.
- `e1()` handles `-a`.
- `e2()` handles `!`.
- `e3()` handles primaries, parentheses, unary predicates, binary string/integer/time operators.
- Evaluation is short-circuited by passing `eval` flags into subexpressions.

Supported checks:
- File: `-f`, `-d`, `-r`, `-w`, `-x`, `-e`, `-s`.
- Plan 9 mode bits: `-A` append-only, `-L` exclusive-use, `-T` temporary.
- TTY: `-t [fd]`.
- Strings: `-n`, `-z`, `=`, `!=`.
- Integers: `-eq`, `-ne`, `-gt`, `-lt`, `-ge`, `-le`.
- Time: `-older`, `-ot`, `-nt`.

Implementation helpers:
- `hasmode()`, `isdir()`, `isreg()`, `fsizep()` use `dirstat`.
- `isatty()` compares fd qid to `/dev/cons`.
- `isolder()` parses duration suffixes `y M d h m s`.
- `synbad()` prints syntax errors and exits `"bad syntax"`.

Risk notes:
- `isolderthan()` and `isnewerthan()` names appear inverted relative to common `-ot`/`-nt` expectations: `isolderthan(a,b)` returns `ad->mtime > bd->mtime`, while `isnewerthan(a,b)` returns `ad->mtime < bd->mtime`.
- Unsupported Unix primaries like `-c`, `-b`, `-u`, `-g` always return false.
