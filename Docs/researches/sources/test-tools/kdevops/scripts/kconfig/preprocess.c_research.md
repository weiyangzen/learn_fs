# sources/test-tools/kdevops/scripts/kconfig/preprocess.c

## Purpose
`preprocess.c` implements Kconfig variable, environment, and function expansion. It supports make-like `$(...)` references, recursive/simple/append variables, user-defined function arguments, built-in functions, shell command expansion, and dependency emission for referenced environment variables.

## Important APIs, Types, And Functions
Public functions are `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`. Internal functions include `env_expand()`, `do_error_if()`, `do_filename()`, `do_info()`, `do_lineno()`, `do_shell()`, `do_warning_if()`, `function_expand()`, `variable_lookup()`, `variable_expand()`, `eval_clause()`, `expand_dollar_with_args()`, and `__expand_string()`.

## Control Flow
Lexer/parser code calls expansion helpers when scanning tokens and assignments. `eval_clause()` splits a `$(name,arg,...)` body on top-level commas, recursively expands name and arguments, then tries local numeric arguments, user variables/functions, built-in functions, and finally environment variables. Recursive variables expand at use time; simple variables expand at assignment time; `+=` inherits existing flavor or defaults to recursive. `env_write_dep()` writes makefile-style guards for each referenced environment variable and frees the environment list.

## State And Persistence
Two global linked lists track referenced environment variables and defined variables. Variables are freed after parse via `variable_all_del()`. Environment references persist into `autoconf_cmd` dependency text rather than files directly. Built-in `$(shell,...)` can observe external system state.

## Dependencies And Integration Points
Depends on Kconfig lexer globals (`cur_filename`, `yylineno`), `struct gstr` helpers from `util.c`, list utilities, `array_size.h`, `xalloc.h`, standard C, and `popen()`. `parser.y` uses `variable_add()` and `env_write_dep()`, while lexer logic typically calls token expansion.

## Risks And Edge Cases
`$(shell,...)` executes arbitrary commands from Kconfig input. Expansion has recursion protection but still allows deep work up to 1000 expansions. `do_shell()` reads only the first 4096 bytes of command output. The local source contains duplicated `struct list_head node;` and an extra closing brace after `expand_dollar()`, likely compile-breaking artifacts. Undefined variables silently expand to empty strings.

## Test Signals
Test recursive/simple/append assignments, positional arguments, nested function calls, built-ins, environment references and dependency output, recursion detection, unterminated references, too many function arguments, shell output newline normalization, and compilation against the lexer/parser.
