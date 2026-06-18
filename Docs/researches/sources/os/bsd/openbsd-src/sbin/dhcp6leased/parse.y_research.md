# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse.y

Yacc grammar and lexer for `dhcp6leased.conf`.

The grammar accepts macro assignments, `request rapid commit`, and `request prefix delegation on <iface> for { ... }` blocks. Delegated target entries are interface names with optional `/prefixlen`, defaulting to `/64`; the special name `reserve` is allowed repeatedly and is later skipped during address configuration.

The parser maintains config queues of requesting interfaces, IA_PD requests, and downstream prefix targets. After parsing it computes an addressing plan that assigns prefix masks to each downstream target and determines the requested upstream prefix length needed to cover them. Duplicate non-reserve target interfaces within an IA are rejected, interface and macro names are length checked, and too many IA requests are rejected at `MAX_IA`.

The lexer supports quoted strings, comments, backslash-newline continuation, numbers, keywords, and `$macro` expansion through an unget buffer. It records line numbers for diagnostics, supports persistent/nonpersistent macros, warns about unused macros at high verbosity, and includes file secrecy checks for secret-capable parsing even though the main config is opened non-secret here.
