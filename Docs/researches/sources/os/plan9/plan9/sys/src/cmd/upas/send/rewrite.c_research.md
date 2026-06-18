# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/rewrite.c

## Purpose
Rewrite-rule parser and matcher for `upas/send` address binding.

## Main Interfaces
- `getrules`: reads `UPASLIB/rewrite`.
- `rule_parse`: token parser with `\l` local-system substitution.
- `rewrite`: matches a destination and fills replacement fields/status.
- `dumprules`: debug dump of loaded rules.

## Behavior
Rules contain a regexp, action type (`|`, `>>`, `alias`, `translate`, `auth`), and one or two replacement expressions. Matching is case-insensitive by lowercasing the address, requires full-string match, lazily compiles regexps, and performs substitutions for capture groups, `&`, `\s` sender/reply address, and `\p` bulk/normal priority. Rules containing `\l` are duplicated for alternate system name.

## Dependencies
`regexp`, `String`, global `thissys`/`altthissys`, `message`, `dest`.

## Risks / Notes
Invalid regexp logs to `mail`; failed rule compilation silently skips that rule during matching.
