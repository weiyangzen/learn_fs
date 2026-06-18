# File Research: sources/os/plan9/plan9/sys/src/9/ip/eipconvtest.c

Standalone test program for the IP/Ethernet formatting conversion logic.

Key behavior:
- Defines local `eipconv` formatter for `%E`, `%I`, `%i`, `%V`, and `%M`.
- Formats Ethernet addresses, IPv4-mapped IPv6 addresses, IPv6 addresses with longest-zero-run elision, IPv4 addresses, and masks as either prefix lengths or full IP strings.
- Includes `prefixvals` and test vectors for IPv4-mapped addresses, all-ones masks, prefix masks, zero masks, and sparse IPv6 values.
- `main` installs `%I` and `%M`, then prints each test vector as an address and mask.

Notable use:
- Mirrors kernel formatter behavior in a user-space style test harness.
