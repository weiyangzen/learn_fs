# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.y

Read fully: 318 lines, 6975 bytes. SHA-256 prefix: `1cb023bf154b42de`.

This Yacc grammar parses inbound SMTP commands and mailbox paths. It recognizes HELO/EHLO, MAIL FROM with optional AUTH parameter, RCPT TO, DATA, RSET, SEND/SOML/SAML, VRFY/EXPN, HELP, NOOP, QUIT, STARTTLS, AUTH, blank lines, and path/mailbox/domain forms.

Actions call daemon functions directly: `hello()`, `sender()`, `receiver()`, `data()`, `reset()`, `verify()`, `help()`, `noop()`, `quit()`, `starttls()`, and `auth()`. Address grammar canonicalizes `local@domain` into Plan 9 bang form `domain!local`; route paths are joined with `!`; empty paths become `/dev/null`.

`parseinit()` prepares a reusable bang token and binds lexer input to the SMTP input `Biobuf`. `yylex()` lowercases alphabetic command bytes, maps CRLF to `CRLF`, whitespace to `SPACE`, control bytes to `CNTRL`, and otherwise returns literal characters. `cat()` assembles `String` values from grammar pieces.

Integration: compiled into the daemon and included through generated `y.tab.h` in `smtpd.c`.

Risk notes: grammar accepts a relatively old SMTP/path model, including source routes and bang paths. It masks input to 7 bits and lowercases letters, which is appropriate for commands but constrains raw path syntax.
