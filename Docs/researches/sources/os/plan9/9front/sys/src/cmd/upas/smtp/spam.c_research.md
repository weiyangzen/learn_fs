# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/spam.c

Despite the filename, this is the SMTP daemon policy/configuration helper. It reads ratify actions, trusted IPs, `smtpd.conf`, local domains, relay settings, blocked sender/account actions, and names blocked lists. It also implements forwarding/masquerade checks, blocked-message dump filenames, and per-recipient spam-filter opt-out.

Actions come from `/mail/ratify/<action>/<type>/<value>` and can allow, block, deny, dial, or delay. `forwarding()` prevents untrusted relay unless the recipient is local or uses loopback syntax. `masquerade()` detects untrusted use of local domains in envelope or headers.

This file supplies much of `smtpd`'s local policy surface and filesystem-backed configuration behavior.
