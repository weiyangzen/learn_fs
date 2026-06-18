# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/dhctoken.h

## Purpose
Defines lexer/parser token values for dhclient configuration and lease files.

## Main Elements
- Single-character token aliases: semicolon, dot, colon, comma, slash, braces.
- Keyword token numeric values beginning at `HOST = 256`.
- Tokens cover host declarations, leases, ranges, network fields, lease dates, server/client options, media, aliases, reject rules, hardware types, VLAN PCP, and ignore rules.
- `is_identifier(x)` helper macro classifies parser identifiers while excluding strings, numbers, and EOF.

## Dependencies And Integration
Used by `parse.c`, `clparse.c`, and the lexer in `conflex.c`. Token values must match keyword recognition and parser switch statements.

## Risk Notes
Token renumbering or collision would break configuration parsing. This file is data-definition only, but parser correctness depends on its stability.
