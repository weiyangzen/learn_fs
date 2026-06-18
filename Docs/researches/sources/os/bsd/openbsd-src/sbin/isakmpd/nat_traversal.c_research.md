# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.c

This file implements IKEv1 NAT traversal negotiation and keepalive scheduling.

Key APIs:
- `nat_t_init()`: precomputes NAT-T vendor ID MD5 hashes.
- `nat_t_add_vendor_payloads(struct message *)`: appends supported NAT-T vendor payloads unless NAT-T is disabled.
- `nat_t_check_vendor_payload(struct message *, struct payload *)`: detects peer NAT-T support from vendor payload hashes and marks payloads consumed.
- `nat_t_exchange_add_nat_d(struct message *)`: adds NAT-D payloads for remote then local addresses.
- `nat_t_exchange_check_nat_d(struct message *)`: compares received NAT-D payloads against local/remote address hashes and sets NAT-T enable/keepalive flags.
- `nat_t_setup_keepalive(struct sa *)`: schedules UDP encapsulation keepalives for a phase 1 SA when applicable.

Behavior and integration:
- `disable_nat_t` globally disables NAT-T support, set by command-line handling elsewhere.
- Supports draft NAT-T and RFC 3947 markers through `isakmp_nat_t_cap`.
- NAT-D hashes are computed as `HASH(CKY-I | CKY-R | IP | Port)` using the negotiated phase 1 hash.
- Payload type switches between RFC `ISAKMP_PAYLOAD_NAT_D` and draft `ISAKMP_PAYLOAD_NAT_D_DRAFT` based on exchange flags.
- Keepalives send through the encapsulated transport inside `struct virtual_transport`; interval comes from `General/NAT-T-Keepalive`, defaulting to 20 seconds.

Risk notes:
- `nat_t_setup_hashes()` allocates persistent hash buffers and is intended to run once; there is no corresponding teardown.
- NAT detection depends on exact sockaddr address/port data from transport methods, so transport address normalization matters.
- Keepalive callback assumes `sa->transport` is a virtual transport with an active `encap` member.
