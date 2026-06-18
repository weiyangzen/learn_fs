# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.h

This header defines the public NAT traversal interface for isakmpd.

Key declarations:
- NAT-T VID identifiers: `VID_DRAFT_V2`, `VID_DRAFT_V2_N`, `VID_DRAFT_V3`, `VID_RFC3947`.
- `struct nat_t_cap`: describes one NAT-T capability marker, including flags, source text, generated hash, and hash length.
- Global `disable_nat_t`.
- Function prototypes for initialization, vendor payload handling, NAT-D generation/checking, and keepalive setup.

Integration:
- Consumed by exchange/message processing code to advertise and detect NAT-T support.
- Depends on `struct message`, `struct payload`, and `struct sa` definitions from other isakmpd headers.

Risk notes:
- The header exposes only the high-level NAT-T operations; capability storage is private to `nat_traversal.c`.
