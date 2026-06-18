# File Research: sources/os/bsd/freebsd-src/sbin/routed/parms.c

Configuration parsing and application for `/etc/gateways`, command-line `-P` options, auth keys, synthetic networks, RIPv1 masks, and trusted gateways.

Key responsibilities:
- Applies matching parameter records to interfaces by name, all interfaces, or address/net match.
- Reads legacy `/etc/gateways` remote/passive/external gateway entries and creates remote interface records.
- Parses parameter lines for RIP, RIPv1/RIPv2, aggregation, router discovery, passive mode, fake defaults, metric adjustment, redirect policy, trusted gateways, and passwords.
- Supports `subnet=` authority routes and `ripv1_mask=` classful compatibility overrides.
- Parses cleartext and MD5 passwords with optional key ID and validity timestamps, accepting MD5 only from secure files.
- Checks parameter conflicts and stores records in operator-specified order.
- Resolves host and network names/numeric forms with optional prefix lengths.

Dependencies:
- Uses `defs.h`, `pathnames.h`, host/network resolver APIs, interface insertion, route mask helpers, and global config lists consumed by interface and RIP logic.

Notable risks:
- Password parsing depends on secure ownership/mode checks only for file-sourced MD5 parameters.
- `parse_quote()` implements custom escaping and delimiter handling used for secrets and parameter values.
- Conflicting overlapping parameter records are allowed only where explicit consistency checks pass; ordering affects final interface state.
