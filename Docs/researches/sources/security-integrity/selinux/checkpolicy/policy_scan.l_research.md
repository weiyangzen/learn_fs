# sources/security-integrity/selinux/checkpolicy/policy_scan.l

## Purpose

`policy_scan.l` is the Flex scanner for SELinux source policy syntax. It recognizes keywords, identifiers, paths, filenames, numbers, IP/CIDR forms, operators, punctuation, comments, whitespace, and `#line` directives. It also owns parser diagnostic location state and warning/error formatting.

## Important APIs and Globals

The scanner defines `source_file`, `source_lineno`, `policydb_lineno`, `policydb_errors`, and `werror`. `yyerror()` prints an error with source file, source line, token, policydb line, and two buffered source lines, then increments `policydb_errors`. `yywarn()` either delegates to `yyerror()` when warnings are fatal or prints a warning. `set_source_file()` and `set_source_line_and_file()` update logical source locations, including preprocessing-style `#line` directives.

For fuzzing builds, `YY_FATAL_ERROR` is redirected to `yyfatal()`, which reports through `yyerror()` and longjmps rather than exiting.

## Control Flow

Lexing is rule ordered. Newline handling captures the next line text into a rotating two-entry `linebuf`, increments policy and source line counters, and uses `yyless(1)` so the newline itself remains available. Keyword rules return named Bison tokens. Generic patterns return `IDENTIFIER`, `NUMBER`, `FILESYSTEM`, `NETIFNAME`, `PATH`, `QPATH`, `FILENAME`, IPv4/IPv6 tokens, and version identifiers. Comments and whitespace are discarded. Operators and punctuation return either named tokens or their character code. Any unrecognized character calls `yyerror()`.

## State and Persistence Behavior

Scanner state is process-global and reset indirectly by `init_parser()` in `policy_define.c`. It does not allocate policy objects. It may mutate `source_file` and line counters during lexing. For quoted paths/filenames, grammar actions later edit `yytext` to strip quotes before queuing.

## Dependencies and Integration Points

The scanner includes the generated parser header (`policy_parse.h` on Android, otherwise `y.tab.h`) so token numbers match the grammar. It integrates with `policy_parse.y` via returned tokens and with `policy_define.c` via `yyerror`, `yywarn`, and source-location globals. It uses standard C library parsing helpers for line directives.

## Risks and Edge Cases

Rule precedence matters. Some token classes overlap, especially identifiers, filesystems, netif names, version identifiers, IPv4 addresses, and numbers. Source line overflow emits warnings. The two-line diagnostic buffer is fixed at 255 bytes per line, so long lines are truncated intentionally. The scanner is not reentrant. Warning-as-error behavior changes control flow by incrementing `policydb_errors`.

## Test Signals

Scanner-focused tests should include every keyword in mixed case where supported, identifiers with underscores/hyphens/dots, invalid characters, quoted paths and filenames, comments, whitespace, long lines, `#line` with and without file names, IPv4/IPv6 and CIDR tokens, version-like strings, and `werror` behavior.
