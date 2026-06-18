# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/rewrite.c

`rewrite.c` loads `/mail/lib/rewrite`, parses rewrite rules, compiles address regexes lazily, and substitutes captured fields into delivery command strings. Rule types map to pipe, mailbox append, alias, translate, and auth destination statuses.

`rule_parse()` expands `\l` to the local or alternate system name; `getrules()` duplicates such rules for `altthissys` when needed. `findrule()` skips authorization rules for already-authorized destinations and requires full-string regex matches.

`substitute()` supports numbered subexpressions, `&`, escaped backslash, `\s` reply address, and `\p` bulk/normal policy text. Regex errors are logged to syslog so broken rewrite rules are visible locally.
