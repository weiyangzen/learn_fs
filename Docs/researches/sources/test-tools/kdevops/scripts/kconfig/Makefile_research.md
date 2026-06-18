# sources/test-tools/kdevops/scripts/kconfig/Makefile

## Purpose
This simplified Makefile builds the embedded standalone Kconfig tools (`conf`, `mconf`, `nconf`) for subtree use in kdevops. It keeps local build rules small while using upstream-like Kconfig source files.

## Important APIs, Types, And Functions
`common-objs` lists shared lexer/parser/configuration objects. `lxdialog` collects ncurses dialog objects for `mconf`. Generated sources are `lexer.lex.c` from `lexer.l` using `flex` and `parser.tab.c/parser.tab.h` from `parser.y` using `bison`. `mconf-cfg.sh` and `nconf-cfg.sh` produce `*conf-cflags`, `*conf-libs`, and `*conf-bin` metadata through `cmd_conf_cfg`.

## Control Flow
The default `kconfig` target builds `conf`, `mconf`, and `nconf`. `conf` links common objects plus `conf.o`; `mconf` and `nconf` depend on discovered curses/menu flags and link their frontend-specific objects. `include $(CURDIR)/Kbuild.include` supplies helper macros such as `read-file` and `cmd`.

## State And Persistence
Build outputs include binaries, objects, generated parser/lexer sources, dependency files, and `*conf-*` flag files. `clean` removes those generated artifacts.

## Dependencies And Integration Points
The Makefile depends on a C compiler, `flex`, `bison`, pkg-config/curses discovery scripts, and the local Kconfig sources. It is the integration point that turns the source bundle into kdevops configuration frontends.

## Risks And Test Signals
The `clean-files += parser.tab.c parser.tab.h .lex.c` entry appears to miss `lexer.lex.c`, leaving a generated file behind. Builds can fail when ncurses discovery scripts cannot find packages or when `Kbuild.include` is missing. Test signals are `make clean`, `make conf`, `make mconf`, `make nconf`, and dependency rebuilds after touching `lexer.l` or `parser.y`.
