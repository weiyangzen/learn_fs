# sources/test-tools/kdevops/scripts/kconfig/parser.y

## Purpose
`parser.y` is the Bison grammar for Kconfig files. It turns lexer tokens into menu tree entries, symbol properties, dependency expressions, variable assignments, source inclusions, help text, and parse-time validation state.

## Important APIs, Types, And Functions
The grammar emits `conf_parse(const char *name)` and `zconfdump(FILE *out)`. Internal helpers include `choice_check_sanity()`, `zconf_endtoken()`, `zconfprint()`, `zconf_error()`, `yyerror()`, `print_quoted_string()`, and `print_symbol()`. It uses `%union` values for strings, symbols, expressions, menus, symbol types, and variable flavors.

## Control Flow
Grammar actions call `menu_add_entry()`, `menu_set_type()`, `menu_add_prompt()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_add_dep()`, `menu_add_visibility()`, `menu_add_menu()`, and `menu_end_menu()` as statements are parsed. `source` delegates to `zconf_nextfile()`. Assignment statements call `variable_add()`. `conf_parse()` initializes scanning and menus, runs `yyparse()`, writes autoconf dependency commands including environment dependencies, deletes variables, ensures `modules_sym` and root menu prompt defaults, finalizes menus, checks recursive dependencies and choice sanity, and exits on parse errors.

## State And Persistence
Parse state includes global `current_menu`, `current_entry`, `current_choice`, `cdebug`, lexer globals (`cur_filename`, `cur_lineno`, `yylineno`), `modules_sym`, `autoconf_cmd`, and `yynerrs`. It builds persistent in-memory menu/symbol structures used by later config I/O; it also prepares dependency command text for generated autoconf metadata.

## Dependencies And Integration Points
Depends on Bison, the Kconfig lexer (`lexer.l` via `zconf_*` scanner functions), `preprocess.c` for variable/function expansion, menu/symbol/expression APIs, and `xalloc`. Frontends and config tools call `conf_parse()` before reading/writing configs.

## Risks And Edge Cases
Nested end-token validation catches mismatched `endif`/`endmenu`/`endchoice` and cross-file endings. Choice members must be bool and prompted. The local source contains duplicated `config_option: T_IMPLY...`, duplicated `fprintf` arguments in `choice_check_sanity()`, and possible copy artifacts that should be compile-checked. Grammar changes can alter Kconfig language compatibility and should be compared to upstream Linux Kconfig.

## Test Signals
Run parser generation/build tests, parse representative Kconfig files with nested menus/ifs/choices, invalid statements, mismatched end tokens, blank/multiple help, `source`, variable assignments, `option modules`, `output yaml`, recursive dependencies, and choice-value defaults outside choices.
