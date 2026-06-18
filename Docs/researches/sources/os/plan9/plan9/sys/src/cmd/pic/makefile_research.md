# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/makefile

Historical makefile for building `pic` outside the Plan 9 mk system. It lists yacc/lexer/generated objects plus geometry, input, output, and utility modules.

`pic` links `picy.o` with object files and `-lm`. Object files depend on `pic.h` and `prevy.tab.h`; `prevy.tab.h` is refreshed from `y.tab.h` only when changed.

Targets include `bundle`, `bowell` deployment, `clean`, and `install` to `/usr/bin/pic`. The file contains two `CFLAGS` assignments, with the later debug/include-path assignment overriding the initial empty one.
