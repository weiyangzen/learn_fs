# File Research: sources/local-fs/jfsutils/missing

GNU Automake `missing` helper script, version `2009-04-28.21`. It is a portability shim used when maintainer tools are absent or too old.

Supported tool fallbacks:
- `aclocal`, `autoconf`, `autoheader`, `automake`, `autom4te`
- `bison`/`yacc`, `flex`/`lex`
- `help2man`, `makeinfo`, `tar`

Behavior:
- With `--run`, tries to execute the requested tool first.
- If the tool is unavailable, prints a warning and touches or creates generated outputs where possible.
- For parser/lexer generators, may copy existing generated `.c`/`.h` files or create trivial stubs.
- For `help2man`, creates an `.ab help2man is required...` stub if needed.
- Exits with failure for unknown unsupported tools.

Filesystem relevance: build-system support only. It can affect regenerated build artifacts, but contains no JFS logic.
