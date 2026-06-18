# File Research: sources/os/bsd/netbsd-src/lib/libc/net/nslexer.l

Flex lexer for `nsswitch.conf`. It skips blanks, comments, and escaped newlines, returns `NL`, status tokens (`SUCCESS`, `UNAVAIL`, `NOTFOUND`, `TRYAGAIN`), action tokens (`RETURN`, `CONTINUE`), and lowercased source/database strings.

String token allocation failures are logged to syslog and converted into a newline token. `_nsyyerror()` logs parse errors with file name, line number, message, and current token text.
