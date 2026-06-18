# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/mxdial.c

Read fully: 385 lines, 7753 bytes. SHA-256 prefix: `7a116d5c7322aba8`.

This file dials SMTP destinations using MX records. `mxdial()` parses a dial string, tries MX hosts for the destination domain, and optionally falls back to a configured gateway only for translation failures.

`mxlookup()` queries `/net/dns` and `/net.alt/dns`, stops on DNS failure, falls back to the host itself when there is no MX record, and resolves one IP per MX for loopback/newline safety checks. `callmx()` sorts MX entries by preference, skips configured busted MX hosts, and dials by MX host name with a 60-second alarm.

`dial_string_parse()` decomposes Plan 9 dial strings into network directory, protocol, host, and service. `$`-prefixed host names are expanded through `/net/cs` `!ipinfo` by `expand_meta()`.

Integration: used by outbound `smtp.c::connect()`. It publishes `dial_string_parse()` through `smtp.h` for TLS/auth host selection.

Risk notes: only the first IP per MX is checked, and the actual dial is by name. Loopback and newline checks reduce DNS abuse, but DNS instability is treated as a retry/permanent distinction by the caller.
