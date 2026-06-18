# sources/test-tools/strace/maint/gen/Makefile

Purpose: standalone makefile for building the strace decoder-definition generator and producing generated decoder C sources from `.def` files.

Important APIs/types/functions: variables `CPPFLAGS`, `TARGET=gen`, object list, dependency files, `GEN_IN=hdio.def`, generated output path `../../src/gen/gen_%.c`, and rules for `flex`, `bison -d`, dependency generation, and cleanup.

Control flow: default target builds `gen` and generated output files. `lex.yy.c` is produced from `lex.l`; `parse.tab.c/h` from `parse.y`; object files link into `gen`; each `defs/%.def` is compiled by running `./gen input output`.

State and persistence behavior: writes build products, generated parser/lexer C, `.d` files, the `gen` executable, and generated decoder files under `src/gen`.

Dependencies and integration points: depends on a C compiler, Flex, Bison, local generator sources, and definition files. The generated C integrates into `src/Makefile.am` through `gen/gen_hdio.c` and `gen/generated.h`.

Risks: dependency inclusion requires `parse.tab.h` ordering. No install target or atomic output for generated C. The makefile is separate from the main Automake flow and can drift.

Test signals: `make` in `maint/gen` should build `gen` and regenerate `src/gen/gen_hdio.c`; `make clean` should remove generated build artifacts.
