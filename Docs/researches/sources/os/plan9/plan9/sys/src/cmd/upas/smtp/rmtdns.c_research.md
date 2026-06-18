# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rmtdns.c

Read fully: 60 lines, 1102 bytes. SHA-256 prefix: `8fe86e36c4cf0a84`.

This file provides `rmtdns()`, a small DNS-existence check for remote path domains. It extracts the domain portion before `!`, accepts bracketed or bare IP literals without lookup, then writes `<domain> all` to `<net>/dns`.

If opening DNS fails, it returns success because the daemon cannot check. If the DNS write fails specifically with `dns: name does not exist`, it returns `-1`; other failures are ignored.

Integration: declared in `smtpd.h`; used by SMTP daemon policy code to verify remote sender domains when enabled.

Risk notes: the function treats DNS infrastructure failures as non-fatal and only distinguishes one exact error string. That policy favors mail availability over strict sender-domain enforcement.
