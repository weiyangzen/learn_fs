# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/parseip.c

Parses IPv4, IPv6, masks, and IPv4 CIDR notation.

Key functions:
- `v4parseip`: parses classful IPv4 shorthand and dotted forms.
- `parseip`: parses IPv4 or IPv6 into 16-byte representation, including `::` elision and IPv4 tails.
- `parseipmask`: accepts `/bits` or address-style masks, including old IPv4 mask style.
- `v4parsecidr`: parses IPv4 address plus optional `/prefix`, defaulting via `defmask`.

Important behavior:
- On parse error, clears `to` to a distinctive zero address and returns `-1`.
- Delimiter logic prevents accidental partial parsing such as interpreting `delete` as `de::`.
