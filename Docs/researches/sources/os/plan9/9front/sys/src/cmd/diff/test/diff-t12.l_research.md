# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t12.l

Small Makefile-style diff fixture.

Key behavior:
- Starts with `# Test HMAC:`.
- Defines `PROG=	hmactest`, `NOMAN=	yes`, `DPADD`, `LDADD`, `CFLAGS`, and `SRCS`.
- Ends with `.include <bsd.prog.mk>`.

Research notes:
- Includes tabs and make syntax, useful for whitespace-sensitive diff tests.
- Stored bytes indicate a trailing-line/newline edge case relative to visible lines.
