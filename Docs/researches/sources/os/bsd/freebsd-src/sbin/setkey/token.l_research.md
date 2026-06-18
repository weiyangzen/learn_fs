# File Research: sources/os/bsd/freebsd-src/sbin/setkey/token.l

## Summary
Lex scanner for `setkey` script syntax. It tokenizes commands, algorithms, protocols, options, address/prefix/port syntax, quoted/hex/decimal/string values, and SPD policy strings.

## Main Elements
- Tracks line numbers for parser diagnostics.
- Defines scanner states for policy strings, authentication algorithms, and encryption algorithms.
- Recognizes SAD commands and SPD commands.
- Recognizes AH/ESP/IPCOMP/TCP protocol names including old AH/ESP forms.
- Maps authentication algorithms such as HMAC-SHA variants, AES-XCBC-MAC, TCP-MD5, CHACHA20-POLY1305, and null.
- Maps encryption algorithms such as null, AES-CBC, AES-CTR, AES-GCM-16, and CHACHA20-POLY1305.
- Recognizes compression algorithms, replay/lifetime/NAT-T/ESN/hardware-interface options, address flags, prefixes, and ports.
- Provides `yyerror()`, `yyfatal()`, and `parse()` entry points.

## Dependencies And Integration
Includes `vchar.h` and generated `y.tab.h`, and supplies tokens consumed by `parse.y`.

## Research Notes
Policy scanning intentionally permits whitespace and newlines inside policy bodies until `;`, incrementing `lineno` for embedded newlines.
