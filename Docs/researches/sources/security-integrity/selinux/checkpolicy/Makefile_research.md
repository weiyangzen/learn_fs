# sources/security-integrity/selinux/checkpolicy/Makefile

Purpose: builds `checkpolicy` and `checkmodule`.

Important variables/targets: uses flex and bison to generate `lex.yy.c` and `y.tab.c`; defines shared parser/compiler objects plus program-specific objects. Targets include `all`, `checkpolicy`, `checkmodule`, pattern object compilation, `test`, `checkobjects` for fuzzing, `install`, `relabel`, and `clean`.

Control flow: `all` builds tools then runs `make -C test`. Generated parser/lexer objects compile with `-Werror` filtered out. `test` runs `./tests/test_roundtrip.sh`.

State and dependencies: depends on static libsepol, parser grammar, scanner, module compiler objects, man pages, and install destinations.

Risks and test signals: generated C warnings are tolerated by filtering `-Werror`. `checkobjects` supports fuzz builds. Roundtrip tests provide functional policy conversion coverage.
