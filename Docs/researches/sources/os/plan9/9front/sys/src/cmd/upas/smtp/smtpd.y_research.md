# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.y

This yacc grammar parses SMTP command conversations. It recognizes HELO/EHLO, MAIL FROM, RCPT TO, DATA, RSET, SEND/SOML/SAML aliases, VRFY/EXPN, HELP, NOOP, QUIT, STARTTLS, and AUTH with or without an initial response.

The grammar converts SMTP path syntax to Plan 9 bang paths, including route-addresses, mailbox domains, local parts, quoted strings, IPv4/IPv6 literals, anonymous `<>` as `/dev/null`, and optional spaces. Lexer input is 7-bit normalized, case-insensitive for alpha commands, and CRLF-aware.

Parser actions call the C handlers in `smtpd.c` directly. `cat()` builds `String` values from token fragments and frees consumed strings.
