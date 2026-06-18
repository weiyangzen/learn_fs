# File Research: sources/virtualization/nbdkit/filters/ip/ip.c

Implements filter glue for source-address and peer-identity access control. It maintains linked lists of allow and deny rules parsed by `rules.c`.

`allow=` and `deny=` may appear multiple times and append comma-separated rules. Config completion only prints parsed rules when debug is enabled. At unload, both lists are freed.

If rules do not require TLS DN inspection, `ip_preconnect()` checks before expensive negotiation. DN and issuer-DN rules set global `late_filtering`, causing checks to occur in `list_exports` and `open`, when TLS peer data is available.

`check_if_allowed()` is default-allow: any allow match permits immediately, otherwise any deny match rejects, otherwise the client is accepted.
