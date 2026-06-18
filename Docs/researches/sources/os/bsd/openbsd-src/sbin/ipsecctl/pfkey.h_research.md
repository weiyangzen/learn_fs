# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.h

This header declares the public PF_KEY interface used by `ipsecctl`.

Key contents:
- Defines `PFKEYV2_CHUNK` as `sizeof(u_int64_t)`, the unit used for SADB message and extension lengths.
- Declares parsing, printing, monitoring, socket initialization, flush, rule establishment, raw dump, and SPI extraction functions.

Declared functions:
- `pfkey_parse`
- `pfkey_print_sa`
- `pfkey_monitor_sa`
- `pfkey_print_raw`
- `pfkey_ipsec_establish`
- `pfkey_ipsec_flush`
- `pfkey_init`
- `pfkey_monitor`
- `pfkey_get_spi`

Dependencies:
- Assumes `struct sadb_msg` and `struct ipsec_rule` are visible to includers.

Research notes:
- This is a small boundary header between PF_KEY implementation/dump code and the rest of `ipsecctl`.
