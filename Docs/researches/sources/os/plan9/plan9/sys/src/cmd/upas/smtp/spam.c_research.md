# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/spam.c

Read fully: 594 lines, 10298 bytes. SHA-256 prefix: `1d9c02aeb8781c38`.

This file implements `smtpd` spam and relay policy support. It reads SMTP daemon config, maps IP/account actions from `/mail/ratify`, tracks trusted networks/domains, checks forwarding/masquerading, validates recipients, handles banned IP CIDRs, and chooses blocked-message dump files.

`getconf()` reads `/mail/lib/smtpd.conf` options such as `norelay`, `verifysenderdom`, `saveblockedmsg`, `defaultdomain`, `ournets`, and `ourdomains`. `blocked()` classifies a sender based on trusted IP, remote-IP action, then lowercased account action. `forwarding()` rejects untrusted relay attempts outside local domains but supports loopback `[]!` rewriting to the remote IP literal.

`masquerade()` detects untrusted senders claiming local domains for warning headers. `recipok()` rejects shell metacharacters, optionally runs `/mail/lib/validateaddress`, and consults `names.blocked`. `optoutofspamfilter()` lets recipients skip spam filtering via `/mail/box/<user>/nospamfiltering`.

Integration: `smtpd.c` calls these routines during MAIL/RCPT/DATA handling. Shared list helpers and daemon globals come from `smtpd.h`.

Risk notes: policy is filesystem-driven and sensitive to exact file layout and config tokenization. CIDR matching is IPv4-only for `ournets`/badguy checks. External validator exit messages determine accept/reject behavior.
