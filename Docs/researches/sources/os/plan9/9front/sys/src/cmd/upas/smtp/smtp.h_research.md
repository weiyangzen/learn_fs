# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.h

`smtp.h` defines shared parser and MX dialing types. `Node` stores token text, token type, address marker, whitespace, and source offsets; `Field` links parsed header fields; `DS`, `Mx`, and `Mxtab` describe dial strings and resolved mail exchangers.

It exports parser globals, parser helper functions, MX dialing functions, and a debug-print macro. This header is shared by the outbound client, inbound server, RFC 822 parser, and parser tests.
