# sources/test-tools/kdevops/scripts/kconfig/lkc.h

## Purpose
`lkc.h` is the central public/internal umbrella header for the standalone Kconfig library. It gathers expression definitions, generated prototypes, scanner interfaces, utility string builders, menu APIs, and symbol APIs.

## Important APIs, Types, And Functions
It includes `expr.h` and `lkc_proto.h`, defines `SRCTREE`, and implements `CONFIG_prefix()` so the `CONFIG_` prefix can be overridden by an environment variable named `CONFIG_`. It declares lexer/parser functions (`zconfdump`, `zconf_starthelp`, `zconf_fopen`, `zconf_initscan`, `zconf_nextfile`, `yylex`), `xfwrite()`, `strhash()`, `file_lookup()`, `struct gstr` and string builder functions, menu construction/query APIs, root menu, and symbol calculation/query APIs.

## Control Flow
The header itself has no control flow except inline helpers. `xfwrite()` asserts nonzero element size and reports write failures. `CONFIG_prefix()` reads the environment at call time, so `CONFIG_` behaves as a dynamic macro.

## State And Persistence
It exposes global `yylineno`, `autoconf_cmd`, and `rootmenu`. Most declared functions mutate parser, menu, symbol, or configuration state elsewhere.

## Dependencies And Integration Points
Every Kconfig implementation file depends on this header for shared prototypes and types. Frontend binaries link code that implements these declarations.

## Risks And Test Signals
The `CONFIG_` environment override is unusual and can alter all config serialization. `xfwrite()` only prints an error rather than aborting. Header changes require full rebuilds of lexer/parser, conf, menuconfig, nconfig, and config I/O tests.
