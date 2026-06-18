# File Research: sources/os/plan9/9front/sys/src/cmd/pic/makefile

This is a legacy Unix-style makefile for `pic`, separate from Plan 9 `mkfile`. It builds `picy.o` plus lexer/parser and generator object files, links with `-lm`, and tracks generated yacc headers with `prevy.tab.h`.

It hardcodes an `lcc` override after an initial generic `cc` setting, so the final active compiler variables are the lcc-oriented ones. Targets include `pic`, `bundle`, `clean`, and `install`, with `install` copying `a.out` to `/usr/bin/pic`.
