# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/testsuite

This rc script exercises SPF macro expansion examples for sender/domain/local-part/IP cases. It runs `mtest` across `%{s}`, `%{o}`, `%{d}` variants, local-part reversal/delimiters, IPv6 `%{i}`, and compound SPF DNS macro forms for both IPv6 and IPv4.

It is a lightweight manual regression fixture rather than a pass/fail harness.
