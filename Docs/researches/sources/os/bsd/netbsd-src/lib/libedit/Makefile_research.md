# File Research: sources/os/bsd/netbsd-src/lib/libedit/Makefile

This makefile builds NetBSD `libedit`.

Key build settings:
- `LIB= edit`
- Depends on `libterminfo`.
- Installs `histedit.h` to `/usr/include`.
- Builds manpages `editline.3`, `editrc.5`, and `editline.7`.
- Installs `libedit.pc` under `/usr/lib/pkgconfig`.

Source list:
- Core sources include `chared.c`, `chartype.c`, `common.c`, `el.c`, `eln.c`, `emacs.c`, `filecomplete.c`, `hist.c`, `history.c`, `historyn.c`, `keymacro.c`, `literal.c`, `map.c`, `parse.c`, `prompt.c`, `read.c`, `readline.c`, `refresh.c`, `search.c`, `sig.c`, `terminal.c`, `tokenizer.c`, `tokenizern.c`, `tty.c`, and `vi.c`.

Generated headers:
- `vi.h`, `emacs.h`, and `common.h` are generated from source files using `makelist -h`.
- `fcns.h`, `func.h`, and `help.h` are generated from the editor command source set.
- The generated headers are prerequisites of `.depend`.

Test hook:
- Defines a build target for `tc1` from `TEST/tc1.c` linked against `libedit.a` and termlib.

Warnings and portability:
- Uses `WARNS?=5`, `-Wunused-parameter`, GCC conversion warnings, and selected per-file warning suppressions.
