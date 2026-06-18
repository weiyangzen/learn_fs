# File Research: sources/os/plan9/plan9/sys/src/cmd/yacc.c

This is the Plan 9 yacc implementation. It reads a yacc grammar, builds LALR parsing states and lookahead sets, resolves conflicts, packs parser action/goto tables, emits C parser tables, then copies the parser skeleton from `/sys/lib/yaccpar` or `/sys/lib/yaccpars`.

Key behavior:
- Uses fixed-size global arrays for grammar symbols, productions, states, lookahead sets, working sets, and packed parser tables.
- `setup` handles options, opens output/temp files, scans declarations, reads grammar rules, copies user `%{...%}` code, handles `%union`, `%type`, precedence declarations, and embedded rule actions.
- `gettok`, `cpycode`, `cpyunion`, `skipcom`, and `cpyact` implement yacc-specific lexical handling and C action copying, including `$`, `$$`, typed semantic values, and named references.
- `cpres`, `cempty`, and `cpfir` compute nonterminal production lists, empty-string derivability, and first sets.
- `stagen`, `closure`, `state`, `putitem`, and `flset` build LR item sets, merge equivalent states, and intern lookahead sets.
- `output`, `wract`, `wrstate`, and `precftn` generate parser actions and diagnostics, including shift/reduce and reduce/reduce conflict reporting.
- `go2out`, `callopt`, `gin`, `stin`, and `nxti` pack shift and goto tables into compact arrays.
- `others`, `warray`, `arout`, and `aoutput` emit `yyact`, `yypact`, `yypgo`, `yyr1`, `yyr2`, `yychk`, `yydef`, token translation tables, and copied parser code.

Important dependencies:
- Plan 9 libraries: `<u.h>`, `<libc.h>`, `<bio.h>`, `<ctype.h>`.
- Parser skeleton files: `/sys/lib/yaccpar` and `/sys/lib/yaccpars`.
- Output conventions: default `y.tab.c`, optional `y.tab.h`, `y.output`, and debug token/state output.

Notable details:
- Token values default into the Unicode private-use range via `PRIVATE`.
- Lookahead bitsets are 32-bit integer arrays sized from terminal count.
- The implementation reuses `mem0` for both production storage and item/state storage, with an explicit portability warning about pointer-vs-int assumptions.
- Temporary files store actions and intermediate table data, then are removed by `cleantmp`.
- Generated parser tables use old yacc conventions such as `yyexca`, `YYNPROD`, `YYPRIVATE`, `YYLAST`, and `YYMAXDEPTH`.
