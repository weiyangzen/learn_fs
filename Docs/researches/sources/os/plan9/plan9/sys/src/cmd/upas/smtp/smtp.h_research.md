# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.h

Read fully: 68 lines, 1375 bytes. SHA-256 prefix: `737c2191145ca250`.

This header defines shared SMTP parser and MX-dialer types. `Node` represents a parsed token with links, token type, address flag, preserved string/whitespace, and original source span. `Field` links parsed header fields. `DS` stores parsed Plan 9 dial-string components.

It also defines `Maxbustedmx`, `Maxdomain`, `YYSTYPE`, parser globals, message summary flags, the busted-MX list, and prototypes for parser/link/address helpers, `mxdial()`, and `dial_string_parse()`.

Integration: used by `smtp.c`, `smtpd.c`, `rfc822.y`, `mxdial.c`, `rmtdns.c`, and greylist code.

Risk notes: `YYSTYPE` and struct fields must match generated parser expectations. Source-span fields are used for byte-level reconstruction, so changing ownership or lifetime assumptions can break message rewriting.
