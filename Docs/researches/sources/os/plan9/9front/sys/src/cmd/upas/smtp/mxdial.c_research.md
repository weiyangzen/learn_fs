# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/mxdial.c

`mxdial.c` resolves and dials SMTP destinations. It parses Plan 9 dial strings, expands `$host` through connection-server data, queries DNS for MX then IP records across `/net` and `/net.alt`, sorts MX records by preference per netdir, resolves MX hosts to IPs, rejects loopback MX targets, skips configured busted MX hosts, and dials each candidate with a timeout.

`mxdial0()` fills an `Mxtab` with candidates and supports a gateway-domain fallback. `mxdial()` returns the open fd and selected `Mx` metadata to the SMTP client.

DNS interaction uses `/net*/dns` files directly with timed writes and reads, so error strings determine retry/permanent behavior upstream.
