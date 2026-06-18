# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_l.l

`iplang_l.l` is the lex scanner for the IP packet description language.

Major behaviors:
- Recognizes whitespace, newlines, braces, semicolons, decimal numbers, single hex digits, colons, comments, quoted strings, and generic tokens.
- Maintains line number, token count, current protocol block (`ipproto`), previous protocol, and a stack for nested protocol contexts.
- Contains a keyword table mapping words such as `interface`, `ipv4`, `tcp`, `udp`, `icmp`, `data`, `send`, IP options, TCP options, security classes, and ICMP type/code names to parser tokens.
- Uses `next_state()` to disambiguate context-sensitive keywords:
  - `sum` becomes IPv4/TCP/UDP checksum token depending on current protocol.
  - `opt` becomes IPv4 or TCP option token.
  - `off` and `len` become protocol-specific fields.
  - `nop`, `eol`, and `ts` are remapped for TCP options inside TCP context.
- `push_proto()`/`pop_proto()` preserve nested protocol context across `{}`.
- `save_token()` duplicates raw token text into `yylval.str`.
- `swallow()` skips full-line comments after newlines.

Errors are fatal through `yyerror()`, which prints the offending text and 1-based line number.
